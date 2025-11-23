# 📊 RAPPORT DE PROJET - Smart City Microservices

**Date :** 22-23 Novembre 2025  
**Projet :** Architecture Microservices pour une Smart City  
**Branche :** `developV1`  
**Équipe :** [Votre nom]

---

## 🎯 OBJECTIF DU PROJET

Créer une **architecture microservices complète** pour une Smart City avec :
- 4 microservices utilisant **4 protocoles différents** (REST, SOAP, GraphQL, gRPC)
- Une **API Gateway centralisée**
- Un **client Web** consommant les services via la Gateway
- Tous les services **conteneurisés avec Docker**

---

## ✅ CE QUI A ÉTÉ RÉALISÉ AUJOURD'HUI

### 🏗️ **1. Architecture Microservices (4 services)**

#### 🚌 **Service Transport (REST - FastAPI)**
- **Port :** 8000
- **Protocole :** REST/HTTP avec JSON
- **Base de données :** SQLite (14 transports)
- **Fonctionnalités :**
  - Liste des transports urbains (Bus, Métro, Tramway, Vélo, Taxi)
  - CRUD complet (Create, Read, Update, Delete)
  - Statuts en temps réel (opérationnel, en maintenance, retard, hors service)
  - Documentation Swagger auto-générée : `/docs`
- **Utilité pour l'utilisateur :** Consulter l'état des transports en temps réel

#### 🌫️ **Service Qualité de l'Air (SOAP - Spyne)**
- **Port :** 8001
- **Protocole :** SOAP/XML avec WSDL
- **Base de données :** SQLite (8 mesures)
- **Fonctionnalités :**
  - Mesures de pollution (PM2.5, PM10, O3, NO2, CO)
  - Calcul de l'indice AQI (Air Quality Index)
  - Filtrage par station de mesure
  - WSDL accessible : `http://localhost:8001/?wsdl`
- **Utilité pour l'utilisateur :** Surveiller la qualité de l'air dans différentes zones

#### 🏛️ **Service Tourisme (GraphQL - Strawberry)**
- **Port :** 8002
- **Protocole :** GraphQL
- **Base de données :** SQLite (10 attractions)
- **Fonctionnalités :**
  - Liste des attractions touristiques (musées, monuments, parcs, restaurants)
  - Requêtes flexibles (choisir les champs souhaités)
  - Filtrage par catégorie, note, prix
  - Playground interactif : `/graphql`
- **Utilité pour l'utilisateur :** Découvrir et filtrer les attractions touristiques

#### 🚑 **Service Urgences (gRPC - Protocol Buffers)**
- **Port :** 50051
- **Protocole :** gRPC (binaire, haute performance)
- **Base de données :** SQLite (8 véhicules + 5 interventions)
- **Fonctionnalités :**
  - Gestion des véhicules d'urgence (ambulances, pompiers, police)
  - Suivi des interventions actives
  - Géolocalisation en temps réel
  - Communication binaire ultra-rapide
- **Utilité pour l'utilisateur :** Suivre les services d'urgence en temps réel

---

### 🌐 **2. API Gateway (FastAPI)**
- **Port :** 8888 (au lieu de 8080 - conflit avec Oracle TNS)
- **Rôle :** Point d'entrée unique pour tous les microservices
- **Fonctionnalités :**
  - Routes unifiées : `/api/transport/*`, `/api/tourism/*`, `/api/air-quality/*`, `/api/emergency/*`
  - Health check global : `/health`
  - Gestion des erreurs centralisée
  - CORS activé pour le client web
- **Avantage :** L'utilisateur accède à tous les services via une seule URL

---

### 💻 **3. Client Web (HTML/CSS/JavaScript + Nginx)**
- **Port :** 80 (http://localhost)
- **Technologies :** HTML5, CSS3, JavaScript Vanilla
- **Interface :**
  - Dashboard moderne avec navigation par onglets
  - Vue d'ensemble avec statut de tous les services
  - Section Transport : Liste, Ajout, Suppression de transports
  - Section Tourisme : Grille d'attractions avec filtres visuels
  - Section Qualité Air : Informations SOAP
  - Section Urgences : Informations gRPC
- **Design :** Gradient violet moderne, cartes animées, responsive

---

### 🐳 **4. Conteneurisation Docker**
- **6 Dockerfiles créés** (un par service + gateway + client)
- **docker-compose.yml** orchestrant tous les services
- **Réseau Docker** privé : `smartcity-network`
- **4 volumes persistants** pour les bases de données SQLite
- **Health checks** automatiques pour REST et GraphQL
- **Auto-restart** en cas d'erreur

---

### 📚 **5. Documentation**
- ✅ `README.md` - Vue d'ensemble du projet
- ✅ `ANALYSE_SERVICES.md` - Analyse des 4 services
- ✅ `ANALYSE_COMPLETE.md` - Comparaison des protocoles
- ✅ `TEST_GRAPHQL.md` - Guide de test GraphQL
- ✅ `TEST_GRPC.md` - Guide de test gRPC
- ✅ `DOCKER_GUIDE.md` - Guide Docker complet
- ✅ `.gitignore` - Exclusion des fichiers temporaires

---

### 🔧 **6. Git & GitHub**
- ✅ Repository créé : `https://github.com/ameny-ga/Smart-City.git`
- ✅ Branche `main` : Version initiale stable
- ✅ Branche `developV1` : Développement de l'architecture Docker
- ✅ 30 fichiers commitées (3375 lignes)
- ✅ `.gitignore` configuré (venv, *.db, *-soapui-project.xml)

---

## 🎓 CE QUE L'UTILISATEUR PEUT FAIRE

### **Via le Client Web (http://localhost)**
1. **Vue d'ensemble** : Voir le statut de tous les services
2. **Transport** :
   - Consulter tous les transports disponibles
   - Voir le statut en temps réel (opérationnel/maintenance/retard)
   - Ajouter un nouveau transport
   - Supprimer un transport
3. **Tourisme** :
   - Parcourir les attractions touristiques
   - Voir les détails (description, adresse, horaires, prix)
   - Filtrer par catégorie
4. **Qualité Air & Urgences** : Informations sur les protocoles SOAP et gRPC

### **Via les APIs directes**
- **REST** : `http://localhost:8000/docs` - Swagger UI
- **GraphQL** : `http://localhost:8002/graphql` - Playground interactif
- **SOAP** : SoapUI avec WSDL `http://localhost:8001/?wsdl`
- **gRPC** : Client Python personnalisé

---

## ⚠️ PROBLÈMES RENCONTRÉS & SOLUTIONS

### **Problème 1 : Service gRPC ne démarrait pas**
- **Cause :** Incompatibilité de version `protobuf` (4.25.1 vs 3.20.3)
- **Solution :** Régénération des fichiers `.proto` dans le Dockerfile avec `protobuf==4.21.12`

### **Problème 2 : Port 8080 déjà utilisé**
- **Cause :** Oracle TNS Listener utilise le port 8080
- **Solution :** API Gateway reconfiguré sur le port 8888

### **Problème 3 : Service SOAP inaccessible depuis Gateway**
- **Cause :** SOAP écoute sur `127.0.0.1` au lieu de `0.0.0.0`
- **Solution :** Modification du binding dans `soap_server.py`

### **Problème 4 : GraphQL - Imports relatifs**
- **Cause :** Manque de fichier `__init__.py` dans le dossier `app/`
- **Solution :** Création de `__init__.py` et ajout d'imports relatifs

### **Problème 5 : Bases de données vides**
- **Cause :** Pas d'initialisation automatique au démarrage
- **Solution :** Scripts `init_db.py` exécutés dans les Dockerfiles

---

## 🔜 À FAIRE DEMAIN

### ✅ **1. Vérifier et corriger le service REST**
- [ ] Tester pourquoi la base de données retourne `[]` malgré l'initialisation
- [ ] Vérifier le chemin de la base SQLite dans le volume Docker
- [ ] S'assurer que `init_db.py` fonctionne correctement

### ✅ **2. Finaliser le service SOAP**
- [ ] Vérifier la connexion depuis l'API Gateway
- [ ] Tester avec SoapUI ou zeep (client Python)

### ✅ **3. Tester l'architecture complète**
- [ ] Lancer : `docker-compose up -d`
- [ ] Tester le client Web : http://localhost
- [ ] Tester l'API Gateway : http://localhost:8888/health
- [ ] Vérifier chaque service individuellement

### ✅ **4. Commit et Merge**
```bash
# Ajouter tous les changements
git add .

# Commit avec message descriptif
git commit -m "feat: Add Docker architecture with API Gateway and Web Client"

# Push vers developV1
git push origin developV1

# Merger vers main (si tout fonctionne)
git checkout main
git merge developV1
git push origin main
```

### ✅ **5. Améliorations optionnelles**
- [ ] Ajouter des tests unitaires
- [ ] Créer un README Docker plus détaillé
- [ ] Ajouter des variables d'environnement configurables
- [ ] Implémenter l'authentification JWT
- [ ] Ajouter des métriques (Prometheus/Grafana)

---

## 📋 COMMANDES IMPORTANTES

### **Démarrer l'architecture Docker**
```powershell
docker-compose up -d
```

### **Arrêter tous les services**
```powershell
docker-compose down
```

### **Arrêter et supprimer les volumes (⚠️ supprime les données)**
```powershell
docker-compose down -v
```

### **Voir les logs**
```powershell
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f service-rest
docker-compose logs -f api-gateway
```

### **Reconstruire un service**
```powershell
docker-compose build service-rest
docker-compose up -d service-rest
```

### **Vérifier le statut**
```powershell
docker-compose ps
```

---

## 🎯 DOMAINE DU PROJET

**Secteur :** Ville intelligente (Smart City)  
**Problématique :** Comment intégrer différents services urbains dans une architecture modulaire et scalable ?

**Services couverts :**
1. 🚌 **Mobilité urbaine** - Optimiser les déplacements
2. 🌫️ **Environnement** - Surveiller la pollution
3. 🏛️ **Tourisme** - Valoriser le patrimoine
4. 🚑 **Sécurité** - Coordonner les urgences

**Bénéfices pour la ville :**
- Architecture modulaire et évolutive
- Indépendance technologique (4 protocoles différents)
- Scalabilité (chaque service peut être déployé indépendamment)
- Monitoring centralisé via API Gateway
- Expérience utilisateur unifiée via le client Web

---

## ⚠️ AVANT DE FERMER VS CODE

### **Toujours arrêter les conteneurs Docker :**
```powershell
cd D:\Projet_SmartCity
docker-compose down
```

### **Vérifier qu'ils sont bien arrêtés :**
```powershell
docker ps
# Doit retourner une liste vide
```

### **Si des conteneurs persistent :**
```powershell
docker stop $(docker ps -q)
```

---

## 📊 STATISTIQUES

- **Lignes de code :** ~3500+
- **Fichiers créés :** 40+
- **Services :** 6 (4 microservices + gateway + client)
- **Technologies :** Python, FastAPI, Spyne, Strawberry, gRPC, Docker, Nginx, JavaScript
- **Bases de données :** 4 SQLite indépendantes
- **Durée :** ~8 heures de développement

---

## 🏆 COMPÉTENCES DÉMONTRÉES

✅ Architecture microservices  
✅ Protocoles REST, SOAP, GraphQL, gRPC  
✅ Conteneurisation Docker  
✅ API Gateway pattern  
✅ Développement Full Stack (Backend + Frontend)  
✅ Bases de données relationnelles (SQLite)  
✅ Git & GitHub (branching, merging)  
✅ Documentation technique  
✅ Résolution de problèmes complexes  

---

**🎉 FÉLICITATIONS ! Vous avez créé une architecture microservices professionnelle pour une Smart City !**
