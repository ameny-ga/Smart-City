# Script pour générer les fichiers protobuf
# Exécuter: python generate_proto.py

import os
import subprocess
import shutil

# Chemins
PROTO_SOURCE = "../service_grpc_urgence/app/emergency.proto"
PROTO_DEST_DIR = "proto"

print("🔧 Génération des fichiers protobuf pour le Gateway...")

# Créer le répertoire proto
os.makedirs(PROTO_DEST_DIR, exist_ok=True)

# Copier le fichier .proto
proto_file = os.path.join(PROTO_DEST_DIR, "emergency.proto")
shutil.copy(PROTO_SOURCE, proto_file)
print(f"✅ Copie de {PROTO_SOURCE} vers {proto_file}")

# Générer les fichiers Python
cmd = [
    "python", "-m", "grpc_tools.protoc",
    f"-I{PROTO_DEST_DIR}",
    f"--python_out={PROTO_DEST_DIR}",
    f"--grpc_python_out={PROTO_DEST_DIR}",
    proto_file
]

print(f"🔨 Exécution: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Fichiers protobuf générés avec succès!")
    print(f"   - {os.path.join(PROTO_DEST_DIR, 'emergency_pb2.py')}")
    print(f"   - {os.path.join(PROTO_DEST_DIR, 'emergency_pb2_grpc.py')}")
else:
    print(f"❌ Erreur lors de la génération:")
    print(result.stderr)
    exit(1)
