# 🏛️ Guide de Test GraphQL Playground

## 🌐 Accès au Playground

Ouvrez dans votre navigateur : **http://127.0.0.1:8002/graphql**

---

## 📝 Exemples de Requêtes GraphQL

### 1️⃣ **Récupérer toutes les attractions**

```graphql
query {
  attractions {
    id
    name
    category
    rating
    city
    address
  }
}
```

---

### 2️⃣ **Récupérer une attraction par ID**

```graphql
query {
  attraction(id: 1) {
    id
    name
    category
    description
    rating
    priceLevel
    openingHours
    phone
    website
    latitude
    longitude
  }
}
```

---

### 3️⃣ **Filtrer les attractions par ville**

```graphql
query {
  attractions(city: "Paris") {
    id
    name
    category
    rating
    address
  }
}
```

---

### 4️⃣ **Filtrer par catégorie (museums uniquement)**

```graphql
query {
  attractions(category: "museum") {
    id
    name
    rating
    openingHours
    website
  }
}
```

---

### 5️⃣ **Attractions avec note minimale de 4.5**

```graphql
query {
  attractionsByRating(minRating: 4.5) {
    id
    name
    rating
    category
    city
  }
}
```

---

### 6️⃣ **Créer une nouvelle attraction (Mutation)**

```graphql
mutation {
  createAttraction(input: {
    name: "Musée d'Art Moderne"
    category: "museum"
    description: "Collection d'art moderne et contemporain"
    address: "11 Avenue du Président Wilson, 75116"
    city: "Paris"
    latitude: 48.8647
    longitude: 2.2978
    rating: 4.5
    priceLevel: 2
    openingHours: "10h-18h (fermé lundi)"
    phone: "+33 1 47 23 61 27"
    website: "https://www.mam.paris.fr"
    isOpen: "open"
  }) {
    id
    name
    category
    rating
  }
}
```

---

### 7️⃣ **Mettre à jour une attraction**

```graphql
mutation {
  updateAttraction(id: 1, input: {
    rating: 4.8
    openingHours: "9h-19h (fermé mardi)"
  }) {
    id
    name
    rating
    openingHours
  }
}
```

---

### 8️⃣ **Supprimer une attraction**

```graphql
mutation {
  deleteAttraction(id: 11)
}
```

---

### 9️⃣ **Requête complexe avec tous les champs**

```graphql
query AllAttractionDetails {
  attractions {
    id
    name
    category
    description
    address
    city
    latitude
    longitude
    rating
    priceLevel
    openingHours
    phone
    website
    imageUrl
    isOpen
  }
}
```

---

### 🔟 **Filtres combinés (ville + catégorie)**

```graphql
query {
  attractions(city: "Paris", category: "monument") {
    id
    name
    rating
    address
    openingHours
  }
}
```

---

## 🎯 Catégories disponibles

- `museum` - Musées
- `monument` - Monuments historiques
- `park` - Parcs et jardins
- `restaurant` - Restaurants
- `hotel` - Hôtels

---

## 📊 Niveaux de prix (priceLevel)

- `1` = € (Économique)
- `2` = €€ (Modéré)
- `3` = €€€ (Cher)
- `4` = €€€€ (Très cher)

---

## 🔍 Statuts (isOpen)

- `open` - Ouvert
- `closed` - Fermé
- `temporarily_closed` - Temporairement fermé

---

## 💡 Astuces Playground

1. **Auto-complétion** : Appuyez sur `Ctrl+Space` pour voir les suggestions
2. **Documentation** : Cliquez sur "DOCS" ou "SCHEMA" à droite pour explorer l'API
3. **Historique** : Vos requêtes sont sauvegardées automatiquement
4. **Variables** : Utilisez l'onglet "Query Variables" pour les paramètres dynamiques
5. **Prettify** : Cliquez sur le bouton "Prettify" pour formater votre requête

---

## ✅ Test rapide

Copiez-collez cette requête dans le playground et cliquez sur le bouton ▶️ :

```graphql
{
  attractions(category: "museum") {
    name
    rating
  }
}
```

Vous devriez voir les musées avec leurs notes ! 🎉
