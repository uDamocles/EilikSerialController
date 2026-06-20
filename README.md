
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

## ⌨️ Control Menu Mapping

The interactive script binds keyboard keys to specific motor positions for real-time puppeteering. Here is the complete list of available commands:

    --- EILIK CONTROL MENU ---
    [a] Left Arm High
    [z] Left Arm 66
    [e] Left Arm Middle
    [r] Left Arm 33
    [t] Left Arm Low
    [y] Right Arm High
    [u] Right Arm 66
    [i] Right Arm Middle
    [o] Right Arm 33
    [p] Right Arm Low
    [q] Head Left
    [s] Head Mid-Left
    [d] Head Middle
    [f] Head Mid-Right
    [g] Head Right
    [w] Torso Left
    [x] Torso Mid-Left
    [c] Torso Middle
    [v] Torso Mid-Right
    [b] Torso Right
    [0] FULL RESET (Middle)
    [!] Quit

---

## 🧠 Interactive Controller Logic (V15)

The interactive control script relies on three technical pillars to ensure fluidity:
1. **Asynchronous Keep-Alive:** A background thread periodically sends the `HB1` command every 2 seconds. This keeps the connection alive and prevents Eilik from reverting to its autonomous mode due to an inactivity time-out.
2. **Non-Blocking Input:** By using system-level libraries (`termios` and `tty` on macOS/Linux), the script captures keystrokes instantly, eliminating the need to press the "Enter" key after each command.
3. **Dynamic Console Interface:** The display leverages ANSI escape sequences (`\r` for carriage return and `\033[K` to clear the line) to dynamically update the execution status on a single line.

<br>

---
---

<br>

# 🇫🇷 Eilik Serial Controller (Version Française)

## 📖 À propos
Ce projet fournit un système de contrôle personnalisé pour le **robot Eilik**. En interagissant directement avec le matériel du robot via son port série USB, ce script contourne le logiciel propriétaire pour obtenir un contrôle total et en temps réel de ses servomoteurs.

> ⚠️ **État du projet & Feuille de route :** Pour l'instant, il s'agit d'un programme très basique qui se concentre exclusivement sur la gestion des servomoteurs. L'objectif futur est d'étendre ses capacités pour piloter également l'affichage sur l'écran, le microphone ainsi que le haut-parleur.

## ⚙️ Fonctionnalités
* **Contrôle Matériel Direct :** Contournement de l'application officielle via l'envoi de trames hexadécimales brutes.
* **Bypass Anti-Rejeu :** Handshake automatisé et extraction dynamique du jeton de session.
* **Réactivité Temps Réel :** Entrées clavier non bloquantes pour une réaction immédiate des moteurs.
* **Interface Console Dynamique :** Mise à jour propre du statut sur une seule ligne.

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

## ⌨️ Mapping des Touches (Menu)

Le script interactif associe les touches du clavier à des positions de moteurs spécifiques pour un pilotage en temps réel. Voici la liste complète des commandes :

    --- MENU DE CONTRÔLE EILIK ---
    [a] Bras Gauche Haut
    [z] Bras Gauche 66
    [e] Bras Gauche Milieu
    [r] Bras Gauche 33
    [t] Bras Gauche Bas
    [y] Bras Droit Haut
    [u] Bras Droit 66
    [i] Bras Droit Milieu
    [o] Bras Droit 33
    [p] Bras Droit Bas
    [q] Tête Gauche
    [s] Tête Milieu-Gauche
    [d] Tête Milieu
    [f] Tête Milieu-Droite
    [g] Tête Droite
    [w] Buste Gauche
    [x] Buste Milieu-Gauche
    [c] Buste Milieu
    [v] Buste Milieu-Droite
    [b] Buste Droite
    [0] RESET COMPLET (Milieu)
    [!] Quitter

---

## 🧠 Fonctionnement du Contrôleur Interactif (V15)

Le script de contrôle interactif repose sur trois piliers techniques :
1. **Keep-Alive Asynchrone :** Un thread fonctionnant en arrière-plan renvoie la commande `HB1` toutes les 2 secondes. Cela maintient la session active et empêche Eilik de repasser en mode autonome.
2. **Entrée Clavier Non-Bloquante :** L'utilisation des bibliothèques systèmes (`termios` et `tty` sous macOS/Linux) permet d'intercepter les frappes au clavier instantanément, sans avoir à valider par la touche "Entrée".
3. **Interface Console Dynamique :** L'affichage utilise les séquences d'échappement ANSI (`\r` pour le retour chariot et `\033[K` pour effacer la ligne) pour rafraîchir le statut de la commande en temps réel sur une seule ligne.
