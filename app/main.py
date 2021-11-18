from typing import List, Optional
from pydantic import BaseModel, IPvAnyAddress, ValidationError
import requests
import json
from config import settings


class IP(BaseModel):
    ip_addr: IPvAnyAddress


class Record(BaseModel):
    type: str
    id: str
    created: str
    modified: str
    zone_id: str
    name: str
    value: str
    ttl: Optional[int]


class RecordResponse(BaseModel):
    record: Record


API_ENDPOINTS = ["https://api.ipify.org", "https://ipv4.icanhazip.com/"]


def get_zone_id(domain: str) -> str:
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/zones",
            params={"name": domain},
            headers={
                "Auth-API-Token": settings.HETZNER_API_TOKEN,
            },
        )
        data = response.json()
        return data["zones"][0]["id"]
    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def get_record_id(zone_id: str, subdomain: str) -> str:
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/records",
            params={
                "zone_id": f"{zone_id}",
            },
            headers={
                "Auth-API-Token": settings.HETZNER_API_TOKEN,
            },
        )
        data = response.json()
        for record in data["records"]:
            name = record["name"]
            if name == subdomain:
                return record["id"]
        raise Exception(f"No record id found matching '{subdomain}'")
    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def get_ip(api_endpoints: List[str]) -> str:
    for endpoint in api_endpoints:
        try:
            response = requests.get(
                url=endpoint,
            )
            ip_addr = str(response.content.decode("utf-8"))
            try:
                IP(ip_addr=ip_addr)
                return ip_addr
            except ValidationError:
                pass
        except requests.exceptions.RequestException:
            print("HTTP Request failed")
    raise Exception("IP address not found")


def get_record(record_id: str) -> RecordResponse:
    try:
        response = requests.get(
            url=f"https://dns.hetzner.com/api/v1/records/{record_id}",
            headers={
                "Auth-API-Token": settings.HETZNER_API_TOKEN,
            },
        )
        data = response.json()
        try:
            record = RecordResponse(**data)
            return record
        except ValidationError:
            print("Could not parse record response")
    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def update_record(
    record_id: str,
    zone_id: str,
    ip_addr: str,
    name: str,
) -> None:
    try:
        requests.put(
            url=f"https://dns.hetzner.com/api/v1/records/{record_id}",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": settings.HETZNER_API_TOKEN,
            },
            data=json.dumps(
                {
                    "value": ip_addr,
                    "ttl": 86400,
                    "type": "A",
                    "name": name,
                    "zone_id": zone_id,
                }
            ),
        )
        print("Updated IP")
    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def main() -> None:
    zone_id = get_zone_id(settings.DOMAIN)
    record_id = get_record_id(zone_id=zone_id, subdomain=settings.SUBDOMAIN)
    record = get_record(record_id=record_id)
    ip_address = get_ip(API_ENDPOINTS)
    if record.record.value != ip_address:
        update_record(
            record_id=record_id,
            zone_id=zone_id,
            ip_addr=ip_address,
            name=settings.SUBDOMAIN,
        )


if __name__ == "__main__":
    main()
