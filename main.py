from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel

app = FastAPI(title="Inventario de red")


class Dispositivo(BaseModel):
    nombre: str
    tipo: str
    ip: str
    activo: bool = True


class DispositivoParcial(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    ip: str | None = None
    activo: bool | None = None


inventario = [
    Dispositivo(nombre="R1", tipo="router", ip="10.0.0.1"),
    Dispositivo(nombre="SW1", tipo="switch", ip="10.0.0.10", activo=False),
    Dispositivo(nombre="FW1", tipo="firewall", ip="10.0.0.254"),
]


def buscar(nombre: str) -> Dispositivo | None:
    for equipo in inventario:
        if equipo.nombre.upper() == nombre.upper():
            return equipo
    return None


@app.get("/dispositivos")
async def listar(activo: bool | None = None):
    if activo is None:
        return inventario
    return [equipo for equipo in inventario if equipo.activo == activo]


@app.get("/dispositivos/{nombre}")
async def obtener(nombre: str):
    equipo = buscar(nombre)

    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el equipo {nombre}",
        )

    return equipo


@app.post("/dispositivos", status_code=status.HTTP_201_CREATED)
async def crear(equipo: Dispositivo):
    if buscar(equipo.nombre) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe el equipo {equipo.nombre}",
        )

    inventario.append(equipo)
    return equipo


@app.put("/dispositivos/{nombre}")
async def reemplazar(nombre: str, datos: Dispositivo):
    equipo = buscar(nombre)

    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el equipo {nombre}",
        )

    if datos.nombre.upper() != nombre.upper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre del dispositivo no puede cambiar",
        )

    indice = inventario.index(equipo)
    inventario[indice] = datos

    return datos


@app.patch("/dispositivos/{nombre}")
async def actualizar(nombre: str, datos: DispositivoParcial):
    equipo = buscar(nombre)

    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el equipo {nombre}",
        )

    cambios = datos.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        if valor is not None:
            setattr(equipo, campo, valor)

    return equipo


@app.delete("/dispositivos/{nombre}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(nombre: str):
    equipo = buscar(nombre)

    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el equipo {nombre}",
        )

    inventario.remove(equipo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)