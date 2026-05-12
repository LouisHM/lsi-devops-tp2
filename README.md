# TP DevOps - Ansible : Déploiement d'une stack Flask + MySQL + Nginx

Projet d'automatisation du déploiement d'une application **Flask** avec une base de données **MySQL** et un reverse proxy **Nginx**, via Ansible et des tests Molecule.

## Membres du binôme

- Louis Maury

## Application déployée

**Flask Hello World API** — une API HTTP minimaliste en Python/Flask qui :
- Expose `GET /` → retourne `Hello DevOps!`
- Expose `GET /health` → vérifie la connectivité MySQL et retourne un JSON de statut
- Tourne en tant que service systemd sur le port **5000**
- Est exposée via un reverse proxy Nginx sur le port **80**

Pour lancer manuellement (sur la VM) :
```bash
cd /opt/devops-app
DB_HOST=localhost DB_USER=appuser DB_PASSWORD=devops_app_pass DB_NAME=devopsapp \
  ./venv/bin/python app.py
```

## Bonus implémentés

| # | Bonus | Description |
|---|---|---|
| 4.1 | **Ansible Vault** | Secrets MySQL chiffrés dans `group_vars/*/vault.yml`, aucun mot de passe en clair |
| 4.2 | **Multi-environnements** | Inventaires et group_vars distincts pour `staging` et `prod` |
| 4.3 | **Certbot** | `geerlingguy.certbot` installé, renouvellement auto, activation conditionnelle en prod |
| 4.4 | **Maildev** | Serveur SMTP de dev (port 1025) avec interface web nginx (port 1080) |
| 4.5 | **Postfix** | MTA configuré en loopback-only via template Jinja2, activé en prod |
| 4.6 | **Backup** | Script `mysqldump` + archive `tar.gz`, rotation 7j, cron quotidien à 2h |

---

## Prérequis système

| Outil | Version minimale | Vérification |
|---|---|---|
| Python | 3.12+ | `python3.12 --version` |
| VirtualBox | 7.0+ | `vboxmanage --version` |
| Vagrant | 2.4+ | `vagrant --version` |

**macOS** — installation via Homebrew :
```bash
brew install --cask virtualbox vagrant
```

---

## Mise en place de l'environnement

```bash
# 1. Activer le virtualenv Python (crée si absent, installe les dépendances)
source venv.sh

# 2. Télécharger les rôles et collections Galaxy
download_galaxy

# 3. Créer le fichier de mot de passe vault (ne jamais committer !)
echo "password" > .devops_vault_pass.txt
```

Fonctions disponibles après `source venv.sh` :
- `download_galaxy` — télécharge rôles (`roles/`) et collections (`.ansible/collections/`)
- `rebuild_env` — recrée le virtualenv depuis zéro
- `deactivate` — quitte l'environnement virtuel

---

## Structure du projet

```
.
├── hosts/
│   ├── hosts_dev              # Inventaire dev (Molecule)
│   ├── hosts_staging          # Inventaire staging
│   └── hosts_prod             # Inventaire production
├── group_vars/
│   ├── all.yml                # Variables globales
│   ├── api.yml                # Config Flask
│   ├── database.yml           # Config MySQL
│   ├── devops_dev/            # Overrides dev + vault chiffré
│   ├── devops_staging/        # Overrides staging + vault chiffré
│   └── devops_prod/           # Overrides prod + vault chiffré + certbot
├── roles/
│   ├── requirements.yml       # Rôles Galaxy (nginx, mysql, certbot)
│   ├── runtime/               # Python 3 + pip + venv
│   ├── app/                   # Flask comme service systemd
│   ├── webserver/             # nginx reverse proxy (Jinja2)
│   ├── database/              # MySQL
│   ├── maildev/               # Maildev SMTP dev + interface web
│   ├── postfix/               # Postfix MTA (Jinja2)
│   └── backup/                # Backup DB + fichiers + cron
├── collections/
│   └── requirements.yml       # community.mysql, community.general
├── molecule/default/          # Scénario Molecule (Vagrant + VirtualBox)
├── playbook_install.yml       # Playbook principal
└── venv.sh                    # Initialisation de l'environnement Python
```

---

## Tests avec Molecule

```bash
# Créer la VM et appliquer le playbook
molecule converge

# Vérifier que tous les services sont up
molecule verify

# Cycle complet (create → converge → idempotence → verify → destroy)
molecule test

# Se connecter à la VM de test
molecule login
```

Les tests (`molecule/default/tests/test_app.py`) vérifient :
- nginx actif (ports 80, 8080)
- MySQL actif (socket Unix)
- Service `devops-app` actif (port 5000) + réponse HTTP `Hello DevOps`
- Maildev actif (SMTP:1025, web:1080)
- Postfix actif (port 25)
- Script backup présent, répertoire créé, cron planifié

---

## Qualité du code

```bash
# Linter Ansible (playbooks + rôles)
ansible-lint -c .ansible-lint.yml playbook_install.yml roles/runtime roles/app roles/webserver roles/database

# Linter Python (tests Molecule)
flake8 -v
```

---

## Déploiement sur une vraie machine

```bash
ansible-playbook -i hosts/hosts_dev -u devops playbook_install.yml
```

---

## Gestion du vault Ansible

```bash
# Créer un vault pour les secrets
ansible-vault create group_vars/devops_dev/vault.yml

# Editer un vault existant
ansible-vault edit group_vars/devops_dev/vault.yml
```

> **Important :** le fichier `.devops_vault_pass.txt` ne doit jamais être commité (déjà dans `.gitignore`).
