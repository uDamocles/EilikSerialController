
# 🤖 Eilik Serial Controller

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Status](https://img.shields.io/badge/status-working-success)
![Reverse Engineering](https://img.shields.io/badge/reverse%20engineering-hardware-orange)

*🇫🇷 [Version Française ci-dessous](#-eilik-serial-controller-version-française)*

## 📖 About
This project provides a custom control system for the **Eilik robot**. By interacting directly with the robot's hardware via its USB serial port, this script bypasses the proprietary software to achieve full, real-time control over its servomotors.

> ⚠️ **Project Status & Roadmap:** Currently, this is a very basic program focused exclusively on managing the servomotors. Future development goals include expanding support to control the screen display, the microphone, and the loudspeaker.


## ⚙️ Features 
* **Direct Hardware Control:** Bypass the official app to send raw hexadecimal frames. 
* **Anti-Replay Bypass:** Automated handshake and dynamic session token extraction. 
* **Real-Time Responsiveness:** Non-blocking keyboard inputs for immediate motor reaction. 
* **Dynamic Console Interface:** Clean, single-line status updates without terminal spam.

---

## 📦 Installation & Prerequisites

This project requires Python 3 and a few external libraries. You can install the required dependencies using `pip`:

```bash
# Install required libraries
pip3 install pyserial pynput
```
_Note: `tty`, `termios`, `sys`, `time`, and `threading` are built-in Python libraries and do not require manual installation._

## 📡 Communication Architecture

Data exchange between the host computer and Eilik uses a standard serial connection set at **125,000 baud**.

### Handshake & Session Token (Anti-Replay Security)
Eilik utilizes an anti-replay mechanism. To gain control and execute movements, a valid session key must be established:

1. **Request (Heartbeat):** Send the initial `HB1` packet: `aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad`.
2. **Reception:** Capture the robot's reply frame.
3. **Key Extraction:** Isolate the **5 bytes** located immediately after the signature `aa aa aa 0a 00 61`. This dynamic key must be injected into all subsequent motion commands during the session.

### Command Frame Structure
To move a motor, the script constructs a frame following this strict structure:

* **Header:** `aa aa aa 14 00 61`
* **Session Token:** The 5 bytes extracted during the Handshake.
* **Motor Parameters:** `03 01` + `[MOTOR_ID]` + `01`
* **Position:** 2 bytes formatted in *Little-endian* (values ranging from 0 to 3000).
* **Padding:** `00 00 00 00 00`
* **Checksum:** Calculated over the payload (excluding the first three `aa aa aa` header bytes). 

Formula: `255 - (sum(payload) % 256)`

---

## 🦾 Motor Kinematics and Mapping

The robot features 4 individually addressable servomotors. The default resting position for all motors is **1500**. 
> **Note:** The physical mounting of the arms requires mirrored logic (e.g., 2500 moves the right arm down, but the left arm up).

| Motor | ID | Low / Right Posture | Middle Posture | High / Left Posture |
| :--- | :--- | :---: | :---: | :---: |
| **Right Arm** | `1` | 2500 | 1500 | 500 |
| **Left Arm** | `2` | 500 | 1500 | 2500 |
| **Torso** | `3` | 500 | 1500 | 2500 |
| **Head** | `4` | 2500 | 1500 | 500 |

---

## 🧠 Interactive Controller Logic

The project provides two distinct control scripts to suit different piloting styles:

### 1. Fixed Positions (`v15.py`)

This script triggers specific, pre-defined motor positions with a single keystroke.

-   **Input handling:** Relies on system-level libraries (`termios` and `tty` on macOS/Linux) to capture keystrokes instantly without needing to press "Enter".
    
-   **Behavior:** Pressing a key once moves the motor to an exact mapped value (e.g., 500, 1500, 2500).
    

### 2. Continuous Movement (`v18.py`)

This script allows for smooth, continuous, relative motor movement, much like a video game joystick.

-   **Input handling:** Uses the `pynput` library to listen for global keyboard events (Key Press and Key Release).
    
-   **Behavior:** As long as a specific key is held down, the motor's position increments or decrements continuously. When the key is released, the movement stops immediately.
    

### Shared Core Mechanics

Both versions rely on common technical pillars to ensure fluidity:

-   **Asynchronous Keep-Alive:** A background thread periodically sends the `HB1` command every 2 seconds. This keeps the connection alive and prevents Eilik from reverting to its autonomous mode due to an inactivity time-out.
    
-   **Dynamic Console Interface:** The display leverages ANSI escape sequences (`\r` for carriage return and `\033[K` to clear the line) to dynamically update the execution status on a single line.

<br>

---
---

<br>

# 🇫🇷 Eilik Serial Controller (Version Française)

## 📖 À propos
Ce projet fournit un système de contrôle personnalisé pour le **robot Eilik**. En interagissant directement avec le matériel du robot via son port série USB, ce script contourne le logiciel propriétaire pour obtenir un contrôle total et en temps réel de ses servomoteurs.

> ⚠️ **État du projet & Feuille de route :** Pour l'instant, il s'agit d'un programme très basique qui se concentre exclusivement sur la gestion des servomoteurs. L'objectif futur est d'étendre ses capacités pour piloter également l'affichage sur l'écran, le microphone ainsi que le haut-parleur.


## ⚙️ Fonctionnalités

-   **Contrôle Matériel Direct :** Contournement de l'application officielle via l'envoi de trames hexadécimales brutes.
    
-   **Bypass Anti-Rejeu :** Handshake automatisé et extraction dynamique du jeton de session.
    
-   **Réactivité Temps Réel :** Entrées clavier non bloquantes pour une réaction immédiate des moteurs.
    
-   **Interface Console Dynamique :** Mise à jour propre du statut sur une seule ligne.
    

## 📦 Installation & Prérequis

Ce projet nécessite Python 3 ainsi que quelques bibliothèques externes. Vous pouvez installer les dépendances requises à l'aide de `pip` :

Bash

```
# Installation des librairies requises
pip3 install pyserial pynput

```

_Note : `tty`, `termios`, `sys`, `time`, et `threading` sont des bibliothèques Python natives et ne nécessitent aucune installation manuelle._

---

## 📡 Architecture de Communication

La communication entre l'ordinateur et Eilik s'effectue via une liaison série standard configurée à **125 000 baud**.

### Handshake et Jeton de Session (Sécurité Anti-Rejeu)
Eilik intègre un mécanisme de sécurité. Avant d'envoyer la moindre instruction, il est impératif d'obtenir une clé de session valide :

1. **Requête (Heartbeat) :** Envoyer le paquet initial `HB1` : `aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad`.
2. **Réception :** Capturer la trame renvoyée par le robot.
3. **Extraction de la clé :** Isoler les **5 octets** situés immédiatement après la signature `aa aa aa 0a 00 61`. Cette clé dynamique doit être insérée dans toutes les commandes de la session en cours.

### Structure des Trames de Commande
Pour actionner un moteur, le script génère une trame selon la structure suivante :

* **En-tête :** `aa aa aa 14 00 61`
* **Jeton de Session :** Les 5 octets extraits lors du Handshake.
* **Paramètres Moteur :** `03 01` + `[ID_MOTEUR]` + `01`
* **Position :** 2 octets formatés en *Little-endian* (valeur comprise entre 0 et 3000).
* **Padding :** `00 00 00 00 00`
* **Checksum :** Calculé sur le payload (excluant les 3 premiers octets `aa aa aa`). 

Formule : `255 - (sum(payload) % 256)`

---

## 🦾 Cinématique et Mapping des Moteurs

Le robot possède 4 servomoteurs adressables individuellement. La position centrale de repos pour tous les moteurs est **1500**. 
> **Note :** Le montage physique des bras implique un fonctionnement en miroir (ex: 2500 baisse le bras droit, mais lève le bras gauche).

| Moteur | ID | Posture Basse / Droite | Posture Milieu | Posture Haute / Gauche |
| :--- | :--- | :---: | :---: | :---: |
| **Bras Droit** | `1` | 2500 | 1500 | 500 |
| **Bras Gauche** | `2` | 500 | 1500 | 2500 |
| **Buste** | `3` | 500 | 1500 | 2500 |
| **Tête** | `4` | 2500 | 1500 | 500 |

---

## 🧠 Fonctionnement du Contrôleur Interactif (V15)

Le projet propose deux scripts de contrôle distincts pour s'adapter à différents styles de pilotage :

### 1. Positions Fixes (`v15.py`)

Ce script déclenche des positions de moteurs spécifiques et prédéfinies à chaque pression de touche.

-   **Gestion des entrées :** Utilise les bibliothèques systèmes (`termios` et `tty` sous macOS/Linux) pour intercepter les frappes instantanément sans avoir à valider par "Entrée".
    
-   **Comportement :** Une pression unique déplace le moteur vers une valeur exacte mappée (ex: 500, 1500, 2500). Il faut "spammer" les touches pour enchaîner les positions.
    

### 2. Mouvement Continu (`v18.py`)

Ce script permet un mouvement fluide, continu et relatif des moteurs, à la manière d'une manette de jeu vidéo.

-   **Gestion des entrées :** Utilise la bibliothèque `pynput` pour écouter les événements globaux du clavier (Pression et Relâchement de touche).
    
-   **Comportement :** Tant qu'une touche est maintenue enfoncée, la position du moteur s'incrémente ou se décrémente en continu. Dès que la touche est relâchée, le mouvement s'arrête net.
    

### Mécaniques Communes

Les deux versions reposent sur des piliers techniques communs pour assurer la fluidité :

-   **Keep-Alive Asynchrone :** Un thread fonctionnant en arrière-plan renvoie la commande `HB1` toutes les 2 secondes. Cela maintient la session active et empêche Eilik de repasser en mode autonome à cause d'une inactivité.
    
-   **Interface Console Dynamique :** L'affichage utilise les séquences d'échappement ANSI (`\r` pour le retour chariot et `\033[K` pour effacer la ligne) pour rafraîchir le statut de la commande en temps réel sur une seule ligne, évitant d'inonder le terminal.
