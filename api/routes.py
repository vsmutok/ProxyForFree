from fastapi import APIRouter, HTTPException, Query

from api.schemas import (
    ConfigItem,
    ConfigsResponse,
    CountriesResponse,
    MessageResponse,
    StartProxyRequest,
    StatusResponse,
    StopProxyRequest,
)
from api.service import ProxyService

router = APIRouter(prefix="/api/v1", tags=["proxies"])

service = ProxyService()


@router.post("/proxies/start", response_model=MessageResponse, summary="Start a proxy")
def start_proxy(request: StartProxyRequest):
    """
    Start a new proxy instance with the given country, config, and port.
    """
    result = service.start_proxy(request.country, request.config, request.port, request.label)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return MessageResponse(success=True, message=result["message"])


@router.post("/proxies/stop", response_model=MessageResponse, summary="Stop a proxy")
def stop_proxy(request: StopProxyRequest):
    """
    Stop a running proxy on the specified port.
    """
    result = service.stop_proxy(request.port)
    return MessageResponse(success=result["success"], message=result["message"])


@router.post("/proxies/stop-all", response_model=MessageResponse, summary="Stop all proxies")
def stop_all_proxies():
    """
    Stop all running proxy instances.
    """
    result = service.stop_all_proxies()
    return MessageResponse(success=result["success"], message=result["message"])


@router.get("/proxies/status", response_model=StatusResponse, summary="Get status of all proxies")
def get_status():
    """
    Return the status of all running proxy instances.
    """
    result = service.get_status()
    return StatusResponse(**result)


@router.get("/proxies/logs/{port}", summary="Get logs for a proxy")
def get_logs(port: int):
    """
    Get OpenVPN logs for a specific proxy port.
    """
    result = service.get_logs(port)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.get("/countries", response_model=CountriesResponse, summary="List available countries")
def list_countries():
    """
    List all available VPN countries.
    """
    countries = service.list_countries()
    return CountriesResponse(countries=countries, total=len(countries))


@router.get("/configs", response_model=ConfigsResponse, summary="List VPN configs")
def list_configs(country: str | None = Query(None, description="Filter by country name")):
    """
    List available VPN configurations, optionally filtered by country.
    """
    configs = service.list_configs(country)
    items = [ConfigItem(country=c, configs=cfgs) for c, cfgs in configs.items()]
    return ConfigsResponse(items=items, total=len(items))
