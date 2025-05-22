import requests
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

class KSIClient:
    """Client for interacting with the KSÍ SOAP API."""
    
    def __init__(self):
        self.base_url = "https://www2.ksi.is/vefthjonustur/mot.asmx"
        self.headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www2.ksi.is/vefthjonustur/mot/{action}"'
        }

    def _make_soap_request(self, action: str, body_content: str = "") -> Dict:
        """Make a SOAP request to the KSÍ API."""
        soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:tns="http://www2.ksi.is/vefthjonustur/mot/">
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>""".strip()

        headers = self.headers.copy()
        headers['SOAPAction'] = headers['SOAPAction'].format(action=action)
        
        # print(f"\nDebug - Making SOAP request for action: {action}")
        # print(f"Debug - Request URL: {self.base_url}")
        # print(f"Debug - Headers: {headers}")
        # print(f"Debug - Request Body:\n{soap_envelope}")

        response = requests.post(self.base_url, data=soap_envelope, headers=headers)
        #
        # print(f"Debug - Response Status: {response.status_code}")
        # print(f"Debug - Response Headers: {dict(response.headers)}")
        # print(f"Debug - Response Content Length: {len(response.text)}")
        # print(f"Debug - First 500 chars of response:\n{response.text[:500]}")

        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        # Remove namespaces for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        
        # Find the response data based on the action
        if action == 'Flokkur':
            array_elem = root.find('.//ArrayFlokkur')
            if array_elem is not None:
                result = [self._xml_to_dict(item) for item in array_elem.findall('Flokkur')]
                # print(f"\nDebug - Found {len(result)} items in ArrayFlokkur")
                # if result:
                #     print(f"Debug - First item: {result[0]}")
                return result
        elif action == 'MotAflog':  # Get tournaments within age group
            array_elem = root.find('.//ArrayMotAflog')
            if array_elem is not None:
                result = [self._xml_to_dict(item) for item in array_elem.findall('MotAflog')]
                # print(f"\nDebug - Found {len(result)} items in ArrayMotAflog")
                # if result:
                #     print(f"Debug - First item: {result[0]}")
                return result
        elif action == 'MotStada':
            array_elem = root.find('.//ArrayMotStada')
            if array_elem is not None:
                result = [self._xml_to_dict(item) for item in array_elem.findall('MotStada')]
                # print(f"\nDebug - Found {len(result)} items in ArrayMotStada")
                # if result:
                #     print(f"Debug - First item: {result[0]}")
                return result
        elif action == 'MotLeikir':
            array_elem = root.find('.//ArrayMotLeikir')
            if array_elem is not None:
                result = [self._xml_to_dict(item) for item in array_elem.findall('MotLeikur')]
                # print(f"\nDebug - Found {len(result)} items in ArrayMotLeikir")
                # if result:
                #     print(f"Debug - First item: {result[0]}")
                return result
        
        print("Debug - No matching array element found in response")
        return []

    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """Convert XML element to dictionary."""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result

    def get_age_groups(self) -> List[Dict[str, Any]]:
        """Fetch all age groups/divisions (e.g., '1. flokkur', '2. flokkur', etc.)."""
        body = '<tns:Flokkur />'
        return self._make_soap_request('Flokkur', body)

    def get_tournaments_in_age_group(self, age_group_id: int) -> List[Dict[str, Any]]:
        """Fetch all tournaments within a specific age group."""
        body = f'<tns:MotAflog><tns:FlokkurNumer>{age_group_id}</tns:FlokkurNumer></tns:MotAflog>'
        return self._make_soap_request('MotAflog', body)

    def get_tournament_standings(self, tournament_id: int) -> List[Dict[str, Any]]:
        """Fetch standings for a specific tournament."""
        body = f'<tns:MotStada><tns:MotNumer>{tournament_id}</tns:MotNumer></tns:MotStada>'
        return self._make_soap_request('MotStada', body)

    def get_tournament_matches(self, tournament_id: int) -> List[Dict[str, Any]]:
        """Fetch all matches for a specific tournament."""
        body = f'<tns:MotLeikir><tns:MotNumer>{tournament_id}</tns:MotNumer></tns:MotLeikir>'
        matches = self._make_soap_request('MotLeikir', body)
        if matches:
            print(f"\nNumber of matches found: {len(matches)}")
        return matches