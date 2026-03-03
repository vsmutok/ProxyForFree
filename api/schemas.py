from pydantic import BaseModel, Field


class StartProxyRequest(BaseModel):
    country: str = Field(..., description="Country folder name", examples=["usa"])
    config: str = Field(..., description="Config file name (with or without .ovpn)", examples=["us-free-44"])
    port: int = Field(..., description="Port for the proxy", ge=1024, le=65535, examples=[8011])


class StopProxyRequest(BaseModel):
    port: int = Field(..., description="Port of the proxy to stop", ge=1024, le=65535, examples=[8011])


class ProxyInfo(BaseModel):
    port: str
    country: str
    config: str
    tun_interface: str
    tun_ip: str
    start_time: str


class StatusResponse(BaseModel):
    proxies: list[ProxyInfo]
    total: int


class MessageResponse(BaseModel):
    success: bool
    message: str


class CountriesResponse(BaseModel):
    countries: list[str]
    total: int


class ConfigItem(BaseModel):
    country: str
    configs: list[str]


class ConfigsResponse(BaseModel):
    items: list[ConfigItem]
    total: int
