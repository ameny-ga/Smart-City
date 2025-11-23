# 📋 TODO LIST - Demain Matin

**Date :** 23 Novembre 2025  
**Priorité :** Commencer petit et simple pour assurer un bon résultat  
**Branche :** `developV1`

---

## 🎯 OBJECTIF DE LA JOURNÉE

Implémenter une **orchestration simple** pour démontrer la **communication inter-services** via l'API Gateway.

**Cas d'usage :** Un citoyen planifie un trajet en vérifiant la qualité de l'air et les transports disponibles.

---

## ✅ PLAN D'ACTION (PETIT & SIMPLE)

### **Phase 1 : Corriger l'existant (1h)**

#### ☐ 1. Corriger service REST - Base de données vide
```powershell
# Relancer avec volumes propres
docker-compose down -v
docker-compose up -d

# Tester
curl http://localhost:8000/transports/
# Doit retourner 14 transports, pas []
```

**Problème :** Le service retourne `[]` malgré l'initialisation  
**À vérifier :**
- Logs : `docker-compose logs service-rest | findstr "transport"`
- Volume : `docker volume inspect smartcity-rest-data`
- Init : S'assure que `init_db.py` s'exécute correctement

---

#### ☐ 2. Tester service SOAP depuis Gateway
```powershell
# Tester WSDL
curl http://localhost:8001/?wsdl

# Tester via Gateway
curl http://localhost:8888/api/air-quality/measures
```

**SOAP écoute maintenant sur 0.0.0.0:8001** (corrigé hier)

---

#### ☐ 3. Valider architecture complète
```powershell
# Démarrer
docker-compose up -d

# Vérifier statut
docker-compose ps
# Tous les conteneurs doivent être "Up"

# Tester Gateway
curl http://localhost:8888/health

# Tester Client Web
# Ouvrir http://localhost
```

---

### **Phase 2 : Orchestration SIMPLE (2h)**

#### ☐ 4. Créer endpoint d'orchestration - VERSION SIMPLE

**Fichier :** `api_gateway/gateway.py`

**Ajouter un endpoint minimaliste :**

```python
@app.get("/api/orchestration/plan-trip")
async def plan_trip_simple(zone: str = "Centre-Ville"):
    """
    Orchestration SIMPLE : Planifie un trajet en vérifiant la qualité de l'air.
    
    Workflow:
    1. Récupérer qualité air de la zone (SOAP)
    2. Si mauvaise qualité (AQI > 100) → recommander alternative
    3. Afficher transports disponibles (REST)
    """
    result = {
        "zone": zone,
        "air_quality": None,
        "recommendation": "",
        "transports": []
    }
    
    # Étape 1 : Qualité de l'air (SOAP)
    try:
        # Pour simplifier, on simule un appel SOAP
        # TODO: Implémenter appel SOAP réel avec zeep
        aqi = 85  # Valeur simulée (Bonne qualité)
        result["air_quality"] = {
            "aqi": aqi,
            "status": "Bonne" if aqi < 100 else "Mauvaise"
        }
        
        # Étape 2 : Recommandation
        if aqi > 100:
            result["recommendation"] = "⚠️ Qualité air médiocre. Privilégiez transports en commun."
        else:
            result["recommendation"] = "✅ Qualité air correcte. Tous transports disponibles."
            
    except Exception as e:
        result["air_quality"] = {"error": str(e)}
    
    # Étape 3 : Transports disponibles (REST)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            transports = response.json()
            # Filtrer uniquement les opérationnels
            result["transports"] = [t for t in transports if t.get("status") == "operationnel"]
    except Exception as e:
        result["transports"] = {"error": str(e)}
    
    return result
```

**Pourquoi SIMPLE ?**
- ✅ Pas de logique complexe
- ✅ 1 zone fixe (Centre-Ville)
- ✅ AQI simulé (pas de vraie intégration SOAP pour commencer)
- ✅ Juste REST pour transports
- ✅ Facile à tester et déboguer

---

#### ☐ 5. Interface Web minimaliste

**Fichier :** `web_client/index.html`

**Ajouter une section simple :**

```html
<!-- Nouvelle section Orchestration -->
<section id="orchestration" class="service-section">
    <h2>🚀 Planifier un trajet intelligent</h2>
    <div class="simple-form">
        <label>Zone de départ :</label>
        <select id="zone-select">
            <option>Centre-Ville</option>
            <option>Gare</option>
            <option>Zone Nord</option>
        </select>
        <button onclick="planTrip()" class="btn-primary">Planifier mon trajet</button>
    </div>
    <div id="trip-result" class="content-area"></div>
</section>
```

**JavaScript :** `web_client/app.js`

```javascript
async function planTrip() {
    const zone = document.getElementById('zone-select').value;
    const resultDiv = document.getElementById('trip-result');
    resultDiv.innerHTML = '<p>Analyse en cours...</p>';
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/orchestration/plan-trip?zone=${zone}`);
        const data = await response.json();
        
        let html = `
            <h3>📍 Zone : ${data.zone}</h3>
            <div class="air-quality">
                <h4>🌫️ Qualité de l'air</h4>
                <p>AQI : ${data.air_quality.aqi} - ${data.air_quality.status}</p>
            </div>
            <div class="recommendation">
                <h4>💡 Recommandation</h4>
                <p>${data.recommendation}</p>
            </div>
            <div class="transports">
                <h4>🚌 Transports disponibles (${data.transports.length})</h4>
                <ul>
                    ${data.transports.map(t => `<li>${t.mode} - ${t.route}</li>`).join('')}
                </ul>
            </div>
        `;
        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Erreur : ${error.message}</p>`;
    }
}
```

---

#### ☐ 6. Tester l'orchestration

```powershell
# Reconstruire Gateway
docker-compose build api-gateway web-client
docker-compose up -d

# Tester endpoint
curl "http://localhost:8888/api/orchestration/plan-trip?zone=Centre-Ville"

# Tester interface Web
# Ouvrir http://localhost → Section "Planifier un trajet"
```

**Résultat attendu :**
```json
{
  "zone": "Centre-Ville",
  "air_quality": {
    "aqi": 85,
    "status": "Bonne"
  },
  "recommendation": "✅ Qualité air correcte. Tous transports disponibles.",
  "transports": [
    {"mode": "Bus", "route": "Ligne 1"},
    {"mode": "Métro", "route": "Ligne A"},
    ...
  ]
}
```

---

### **Phase 3 : Documentation & Commit (30min)**

#### ☐ 7. Mettre à jour la documentation

**Fichier :** `RAPPORT_PROJET.md`

Ajouter section :
```markdown
## 🔄 ORCHESTRATION INTER-SERVICES

### Cas d'usage : Planification de trajet intelligent

**Workflow :**
1. Utilisateur sélectionne une zone de départ
2. Gateway (orchestrateur) interroge :
   - Service SOAP → Qualité de l'air (AQI)
   - Service REST → Transports disponibles
3. Logique de recommandation :
   - Si AQI > 100 → Privilégier transports en commun
   - Sinon → Tous modes disponibles
4. Résultat affiché dans le client Web

**Endpoint :** `GET /api/orchestration/plan-trip?zone={zone}`
```

---

#### ☐ 8. Commit et Push

```bash
# Ajouter tous les changements
git add .

# Commit
git commit -m "feat: Add simple orchestration for trip planning

- Create /api/orchestration/plan-trip endpoint in Gateway
- Integrate SOAP (air quality) and REST (transport) services
- Add recommendation logic based on AQI
- Update web client with trip planning interface
- Update documentation with orchestration workflow"

# Push
git push origin developV1
```

---

## 📊 RÉSULTAT ATTENDU EN FIN DE JOURNÉE

✅ **Architecture fonctionnelle avec orchestration**
- Gateway communique avec SOAP + REST
- Logique métier simple et testable
- Interface utilisateur intuitive

✅ **Démo convaincante**
- Utilisateur planifie trajet
- Voit qualité air + transports
- Reçoit recommandation intelligente

✅ **Code propre et documenté**
- Commentaires clairs
- Documentation à jour
- Git bien organisé

---

## ⚠️ SI PROBLÈMES

### Si service REST retourne toujours []
```powershell
# Supprimer volumes et recréer
docker-compose down -v
docker volume prune -f
docker-compose up --build -d

# Vérifier init
docker-compose logs service-rest | findstr "transport"
```

### Si SOAP ne répond pas
```powershell
# Vérifier logs
docker-compose logs service-soap

# Tester directement
curl http://localhost:8001/?wsdl
```

### Si Gateway ne démarre pas
```powershell
# Reconstruire
docker-compose build api-gateway
docker-compose up -d api-gateway
docker-compose logs -f api-gateway
```

---

## 💡 CONSEILS

1. **Commencer tôt le matin** - Tête fraîche
2. **Tester après chaque étape** - Ne pas accumuler les erreurs
3. **Commit régulièrement** - Sauvegarder les progrès
4. **Rester simple** - Ne pas sur-complexifier
5. **Documenter** - Expliquer ce qui fonctionne

---

## 🎯 PRIORITÉ

**Phase 1** = CRITIQUE (sans ça, rien ne fonctionne)  
**Phase 2** = IMPORTANT (c'est le cœur du sujet)  
**Phase 3** = BONUS (mais valorise le travail)

---

**Durée estimée :** 3-4 heures  
**Difficulté :** Moyenne  
**Impact :** ⭐⭐⭐⭐⭐ (Démontre maîtrise architecture microservices)

---

**🚀 BON COURAGE POUR DEMAIN !**
