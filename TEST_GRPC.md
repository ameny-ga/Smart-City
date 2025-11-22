# 🚑 Guide de Test gRPC - Service Urgences

## ⚡ Lancement du Service gRPC

### 📍 Terminal 1 - Serveur gRPC

Ouvrez un premier terminal PowerShell et exécutez :

```powershell
cd D:\Projet_SmartCity
.\venv\Scripts\python.exe service_grpc_urgence\app\server.py
```

Vous devriez voir :
```
✅ 8 véhicules et 4 interventions ajoutés
🚑 Service gRPC - Urgences
==================================================
Serveur: 127.0.0.1:50051
Protocol: gRPC
==================================================
```

**⚠️ Gardez ce terminal ouvert !** Le serveur doit rester actif.

---

### 📍 Terminal 2 - Client gRPC (Tests)

Ouvrez un **deuxième** terminal PowerShell et exécutez :

```powershell
cd D:\Projet_SmartCity
.\venv\Scripts\python.exe service_grpc_urgence\app\client.py
```

---

## 📝 Résultats Attendus

Le client va exécuter 6 tests automatiques :

### ✅ Test 1 : Récupérer tous les véhicules
```
✅ Nombre de véhicules: 8
   • AMB-001 (ambulance) - available
   • AMB-002 (ambulance) - on_mission
   • FIRE-001 (fire_truck) - available
```

### ✅ Test 2 : Récupérer un véhicule par ID
```
✅ Véhicule trouvé:
   ID: 1
   Identifiant: AMB-001
   Type: ambulance
   Statut: available
   Station: Hôpital Cochin
   Équipage: 2 personnes
```

### ✅ Test 3 : Ambulances disponibles
```
✅ Ambulances disponibles: 2
   • AMB-001 - Hôpital Cochin
   • AMB-003 - Hôpital Val-de-Grâce
```

### ✅ Test 4 : Interventions actives
```
✅ Interventions actives: 4
   • #1 - MEDICAL
     Priorité: high
     Adresse: 15 Rue de Rivoli, 75001 Paris
     Statut: in_progress
```

### ✅ Test 5 : Créer une intervention
```
✅ Intervention créée:
   ID: 5
   Type: medical
   Priorité: high
   Véhicule assigné: 1
```

### ✅ Test 6 : Mettre à jour un véhicule
```
✅ Statut du véhicule mis à jour:
   AMB-001: on_mission
   Nouvelle position: (48.861, 2.341)
```

---

## 🎯 Types de Véhicules

- `ambulance` - Ambulances SAMU
- `fire_truck` - Camions de pompiers
- `police_car` - Voitures de police

## 📊 Statuts des Véhicules

- `available` - Disponible
- `on_mission` - En intervention
- `maintenance` - En maintenance

## 🚨 Types d'Interventions

- `medical` - Urgence médicale
- `fire` - Incendie
- `crime` - Crime/Délit
- `accident` - Accident de la route

## ⚠️ Priorités

- `low` - Faible
- `medium` - Moyenne
- `high` - Élevée
- `critical` - Critique

---

## 🔧 Tests Manuels avec Python

Si vous voulez créer vos propres tests, voici un exemple :

```python
import grpc
import emergency_pb2
import emergency_pb2_grpc

# Connexion
channel = grpc.insecure_channel('localhost:50051')
stub = emergency_pb2_grpc.EmergencyServiceStub(channel)

# Récupérer tous les véhicules
response = stub.GetAllVehicles(emergency_pb2.Empty())
for vehicle in response.vehicles:
    print(f"{vehicle.identifier}: {vehicle.status}")

# Créer une intervention
new_intervention = emergency_pb2.InterventionInput(
    intervention_type="fire",
    priority="critical",
    address="123 Rue de la Paix",
    latitude=48.8700,
    longitude=2.3300,
    assigned_vehicle_id=3,
    description="Incendie dans un immeuble"
)
response = stub.CreateIntervention(new_intervention)
print(f"Intervention #{response.id} créée")
```

---

## 📦 Base de Données

Le service crée automatiquement `urgence.db` avec :
- **8 véhicules** (3 ambulances, 3 camions pompiers, 2 voitures police)
- **4 interventions** en cours

---

## 🎉 Félicitations !

Vous avez maintenant **4 microservices opérationnels** :

1. ✅ REST (Transport) - Port 8000
2. ✅ SOAP (Qualité Air) - Port 8001
3. ✅ GraphQL (Tourisme) - Port 8002
4. ✅ gRPC (Urgences) - Port 50051

🚀 Votre architecture Smart City est complète !
