# Zero Trust + Identidades Máquina en Microservicios (k3d + Kubernetes + Istio)

Este repositorio implementa un laboratorio reproducible para demostrar la transición desde un modelo **perimetral / implícitamente confiable** hacia un modelo **Zero Trust**, aplicado a una arquitectura de **microservicios** desplegada en Kubernetes.

La demo se alinea con el documento (LaTeX) del curso, especialmente con:
- **Zero Trust**: “deny-by-default” + permisos explícitos.
- **Identidades máquina**: identidad de workloads vía **mTLS** (Istio SPIFFE principal).
- **Policy-as-Code**: políticas declarativas (YAML) versionadas en Git.
- **Detección temprana / observabilidad**: aunque este repo no incluye un SIEM completo, las decisiones de autorización generan señales útiles (403/RBAC, logs de proxy) que habilitan medición y reducción de MTTD cuando se integran a un pipeline de monitoreo.

---

## 1. Arquitectura del laboratorio

### Servicios (HTTP, puerto 8000)
- `gateway`: expone endpoints y consume a `users` y `pay`.
- `users`: endpoint simple `/users`.
- `pay`: endpoint simple `/pay`.

### Namespaces
- `insecure`: sin políticas Istio (baseline “abierto”).
- `secure`: con sidecar injection y políticas Istio.

---

## 2. Requisitos

### En tu máquina
- Docker
- Kubernetes local con **k3d** (cluster sugerido: `zt-demo`)
- kubectl
- Istio instalado en el cluster (control-plane en `istio-system`)

> Nota: En Windows, se recomienda ejecutar k3d/kubectl desde WSL.  
> El repo funciona igual si ya tienes el cluster corriendo en WSL/Linux.

---

## 3. Estructura del repo

- `app/`  
  FastAPI demo (`/health`, `/admin`, `/gateway/users`, `/gateway/pay`)
- `k8s/insecure/`  
  Manifests (Namespace + Deployments + Services)
- `k8s/secure/`  
  Manifests (Namespace con `istio-injection=enabled`)
- `istio/`  
  Políticas de seguridad (mTLS + AuthorizationPolicy)
- `scripts/`  
  Scripts helper (bash) para automatizar despliegues

---

## 4. Build e import de la imagen (k3d)

### 4.1 Build
```bash
bash scripts/01_build_image.sh
```

### 4.2 Import al cluster k3d (evita registry externo)
```bash
bash scripts/02_k3d_import.sh
```

---

## 5. Despliegue baseline (insecure)

### 5.1 Deploy
```bash
bash scripts/03_deploy_insecure.sh
```

### 5.2 Verificación (pods y services)
```bash
kubectl -n insecure get pods -o wide
kubectl -n insecure get svc
```

### 5.3 Pruebas (port-forward)
En una terminal:
```bash
kubectl -n insecure port-forward svc/gateway 18000:8000
```

En otra terminal:
```bash
curl -i http://localhost:18000/health | head -n 20
curl -i http://localhost:18000/admin  | head -n 20
curl -i http://localhost:18000/gateway/users | head -n 20
curl -i http://localhost:18000/gateway/pay   | head -n 20
```

**Resultado esperado (insecure):** todo responde **200 OK**, incluyendo `/admin`.

---

## 6. Despliegue baseline (secure, sin políticas aún)

### 6.1 Deploy
```bash
bash scripts/04_deploy_secure.sh
```

### 6.2 Verificación sidecar (READY 2/2)
```bash
kubectl -n secure get pods
```

> READY debe mostrar `2/2` en gateway/users/pay (app + istio-proxy).

### 6.3 Pruebas baseline (port-forward)
Terminal 1:
```bash
kubectl -n secure port-forward svc/gateway 28000:8000
```

Terminal 2:
```bash
curl -i http://localhost:28000/health | head -n 20
curl -i http://localhost:28000/admin  | head -n 20
curl -i http://localhost:28000/gateway/users | head -n 20
curl -i http://localhost:28000/gateway/pay   | head -n 20
```

**Resultado esperado (secure baseline):** también **200 OK**.  
Esto demuestra que **solo** tener sidecars no es Zero Trust; falta la política.

---

## 7. Aplicar Zero Trust (mTLS STRICT + deny-by-default + allowlist)

### 7.1 Activar mTLS STRICT (identidad máquina)
Aplica:
```bash
kubectl apply -f istio/peerauth-strict.yaml
```

Validar:
```bash
kubectl -n secure get peerauthentication
```

**Qué demuestra:** el tráfico dentro del namespace `secure` requiere mTLS (identidad de workload).  
Istio asigna identidades tipo:
`cluster.local/ns/secure/sa/default`

### 7.2 Deny-by-default (Zero Trust)
Aplica:
```bash
kubectl apply -f istio/authz-deny-by-default.yaml
```

Validar:
```bash
kubectl -n secure get authorizationpolicy
```

**Qué demuestra:** el principio de Zero Trust: “no confiar por defecto” (todo denegado si no hay ALLOW).

### 7.3 Allowlist mínimo (principio de mínimo privilegio)
Permitir solo:
- `/health` y `/gateway/*` en `gateway`
- `gateway` -> `users` y `pay` (por principal mTLS)

Aplica:
```bash
kubectl apply -f istio/authz-allow-gateway-public.yaml
kubectl apply -f istio/authz-allow-gateway-to-users-pay.yaml
```

---

## 8. Pruebas finales (evidencia 200 vs 403)

Con el port-forward del `secure` activo:
```bash
kubectl -n secure port-forward svc/gateway 28000:8000
```

Corre:
```bash
# permitidos
curl -i http://localhost:28000/health | head -n 20
curl -i http://localhost:28000/gateway/users | head -n 20
curl -i http://localhost:28000/gateway/pay   | head -n 20

# bloqueado por Zero Trust (sin policy/JWT)
curl -i http://localhost:28000/admin | head -n 20
```

**Resultado esperado (secure con políticas):**
- `/health` => 200
- `/gateway/users` => 200
- `/gateway/pay` => 200
- `/admin` => **403** (bloqueado)

Esto evidencia:
- **Policy-as-Code** (políticas YAML en Git)
- **Deny-by-default**
- **Mínimo privilegio**
- **Identidad máquina** (mTLS principal permitido gateway->users/pay)

---

## 9. Evidencias (capturas)

Agrega imágenes en `docs/images/` y referencia aquí.

Ejemplos:
- Pods en secure (2/2):  
  ![Pods secure](docs/images/01-pods-secure.png)
- Services:  
  ![Services secure](docs/images/02-services-secure.png)
- Baseline secure (200):  
  ![Baseline secure](docs/images/03-curl-secure-baseline.png)
- Zero Trust bloqueando `/admin` (403):  
  ![AuthZ deny](docs/images/04-authz-deny.png)

---

## 10. Relación con el documento (LaTeX)

- **Zero Trust**: se implementa con `AuthorizationPolicy` deny-by-default + allowlist.
- **Identidades máquina**: se exige mTLS con `PeerAuthentication STRICT` y se autorizan flujos por `principals`.
- **Policy-as-Code**: manifests versionados (`istio/*.yaml`) permiten revisión y auditoría.
- **Detección temprana / MTTD**: aunque no se incluye SIEM, los **eventos de denegación (403/RBAC)** y logs del proxy son señales que, integradas a observabilidad, reducen el tiempo de detección.

---

## 11. Troubleshooting rápido

### “kubectl current-context is not set”
Si estás en WSL como root y no tienes kubeconfig:
```bash
export KUBECONFIG=/root/.config/k3d/kubeconfig-zt-demo.yaml
kubectl config current-context
```

### “sigue dando 200”
Verifica que las policies existan:
```bash
kubectl -n secure get peerauthentication,authorizationpolicy
```

