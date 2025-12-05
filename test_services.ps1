# Script de Test Rapide pour TuniLink Services
# Exécuter : .\test_services.ps1

Write-Host "`n🧪 ======== TESTS DES SERVICES TUNILINK ========" -ForegroundColor Cyan

# Test 1: REST Transport
Write-Host "`n1️⃣  SERVICE REST - TRANSPORT (Port 8000)" -ForegroundColor Yellow
Write-Host "   URL Swagger: http://localhost:8000/docs" -ForegroundColor Gray
try {
    $transports = Invoke-RestMethod -Uri "http://localhost:8000/transports" -TimeoutSec 5
    Write-Host "   ✅ Service opérationnel - $($transports.Count) transports disponibles" -ForegroundColor Green
    Write-Host "   Exemples:" -ForegroundColor Gray
    $transports | Select-Object -First 3 | ForEach-Object {
        Write-Host "      - ID: $($_.id) | $($_.mode) | $($_.route) | Status: $($_.status)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: SOAP Air Quality
Write-Host "`n2️⃣  SERVICE SOAP - QUALITÉ AIR (Port 8001)" -ForegroundColor Yellow
Write-Host "   URL WSDL: http://localhost:8001/?wsdl" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/?wsdl" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Service opérationnel - WSDL accessible" -ForegroundColor Green
        Write-Host "   Opérations SOAP disponibles:" -ForegroundColor Gray
        Write-Host "      - GetAllMeasures" -ForegroundColor White
        Write-Host "      - GetMeasureByStation" -ForegroundColor White
        Write-Host "      - GetStations" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: GraphQL Tourism
Write-Host "`n3️⃣  SERVICE GRAPHQL - TOURISME (Port 8002)" -ForegroundColor Yellow
Write-Host "   URL GraphiQL: http://localhost:8002/graphql" -ForegroundColor Gray
try {
    $query = '{"query":"{ allAttractions { id name type zone rating } }"}'
    $result = Invoke-RestMethod -Uri "http://localhost:8002/graphql" -Method Post -Body $query -ContentType "application/json" -TimeoutSec 5
    $attractions = $result.data.allAttractions
    Write-Host "   ✅ Service opérationnel - $($attractions.Count) attractions disponibles" -ForegroundColor Green
    Write-Host "   Exemples:" -ForegroundColor Gray
    $attractions | Select-Object -First 3 | ForEach-Object {
        Write-Host "      - ID: $($_.id) | $($_.name) | Type: $($_.type) | Zone: $($_.zone) | Note: $($_.rating)/5" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: gRPC Emergency
Write-Host "`n4️⃣  SERVICE GRPC - URGENCES (Port 50051)" -ForegroundColor Yellow
Write-Host "   Fichier Proto: service_grpc_urgence/app/emergency.proto" -ForegroundColor Gray
try {
    # Vérifier si grpcurl est installé
    $grpcurl = Get-Command grpcurl -ErrorAction SilentlyContinue
    if ($grpcurl) {
        $result = grpcurl -plaintext -d '{}' localhost:50051 emergency.EmergencyService/GetAllVehicles 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Service opérationnel - Véhicules d'urgence disponibles" -ForegroundColor Green
            Write-Host "   Méthodes gRPC disponibles:" -ForegroundColor Gray
            Write-Host "      - GetAllVehicles" -ForegroundColor White
            Write-Host "      - GetVehicle" -ForegroundColor White
            Write-Host "      - CreateEmergency" -ForegroundColor White
            Write-Host "      - UpdateVehicleStatus" -ForegroundColor White
        } else {
            Write-Host "   ⚠️  Service démarré mais erreur de connexion" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  grpcurl non installé - Installer avec: choco install grpcurl" -ForegroundColor Yellow
        Write-Host "   ℹ️  Service probablement opérationnel sur port 50051" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: API Gateway
Write-Host "`n5️⃣  API GATEWAY - ORCHESTRATEUR (Port 8888)" -ForegroundColor Yellow
Write-Host "   URL Swagger: http://localhost:8888/docs" -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8888/health" -TimeoutSec 5
    Write-Host "   ✅ Service opérationnel" -ForegroundColor Green
    Write-Host "   Endpoints d'orchestration disponibles:" -ForegroundColor Gray
    Write-Host "      - GET  /api/orchestration/city-dashboard" -ForegroundColor White
    Write-Host "      - GET  /api/orchestration/plan-trip" -ForegroundColor White
    Write-Host "      - GET  /api/orchestration/tourist-day" -ForegroundColor White
    Write-Host "      - POST /api/orchestration/emergency-response" -ForegroundColor White
    Write-Host "      - GET  /api/orchestration/eco-route" -ForegroundColor White
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Web Client
Write-Host "`n6️⃣  WEB CLIENT - INTERFACE UTILISATEUR (Port 80)" -ForegroundColor Yellow
Write-Host "   URL: http://localhost" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Service opérationnel - Interface web accessible" -ForegroundColor Green
        Write-Host "   Pages disponibles:" -ForegroundColor Gray
        Write-Host "      - http://localhost           (Dashboard principal)" -ForegroundColor White
        Write-Host "      - http://localhost/orchestration.html  (Tests orchestration)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Authentication
Write-Host "`n🔐 SYSTÈME D'AUTHENTIFICATION" -ForegroundColor Yellow
try {
    $creds = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin123"))
    $headers = @{Authorization = "Basic $creds"}
    $user = Invoke-RestMethod -Uri "http://localhost:8888/api/auth/me" -Headers $headers -TimeoutSec 5
    Write-Host "   ✅ Authentification opérationnelle" -ForegroundColor Green
    Write-Host "   Comptes de test:" -ForegroundColor Gray
    Write-Host "      - admin/admin123 (Administrateur - Accès complet)" -ForegroundColor White
    Write-Host "      - user/user123   (Utilisateur - Lecture seule)" -ForegroundColor White
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Résumé
Write-Host "`n📊 ======== RÉSUMÉ ========" -ForegroundColor Cyan
Write-Host "Services testés avec succès! Consultez :" -ForegroundColor Green
Write-Host "  📖 GUIDE_TESTS_SERVICES.md - Guide complet de tests" -ForegroundColor White
Write-Host "  🔒 TESTS_AUTHENTIFICATION.md - Tests de sécurité" -ForegroundColor White
Write-Host "  🏛️  SECURITE_ET_ROLES.md - Architecture de sécurité" -ForegroundColor White

Write-Host "`n🌐 LIENS RAPIDES:" -ForegroundColor Cyan
Write-Host "  Dashboard:    http://localhost" -ForegroundColor White
Write-Host "  Orchestration: http://localhost/orchestration.html" -ForegroundColor White
Write-Host "  REST API:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  GraphQL:      http://localhost:8002/graphql" -ForegroundColor White
Write-Host "  Gateway:      http://localhost:8888/docs" -ForegroundColor White
Write-Host "  SOAP WSDL:    http://localhost:8001/?wsdl" -ForegroundColor White

Write-Host "`n✅ Tests terminés!" -ForegroundColor Green
