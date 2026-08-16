"""Deterministic rule checker for common Cisco config mistakes."""

import re
from typing import List, Dict, Any
from src.models import Evidence, Case


class RuleChecker:
    """Deterministic checks for common network configuration errors."""
    
    def __init__(self):
        self.checks = [
            self._check_wrong_subnet_mask,
            self._check_gateway_mismatch,
            self._check_interface_down,
            self._check_missing_vlan,
            self._check_missing_route,
            self._check_dhcp_pool_missing,
            self._check_dhcp_wrong_network,
            self._check_dhcp_wrong_gateway,
            self._check_acl_blocking,
            self._check_nat_missing,
        ]
    
    def run_all_checks(self, evidence: Evidence, case: Case = None) -> List[Dict[str, Any]]:
        """Run all deterministic checks on evidence."""
        results = []
        for check in self.checks:
            try:
                result = check(evidence, case)
                if result:
                    results.append(result)
            except Exception as e:
                results.append({
                    "check": check.__name__,
                    "status": "ERROR",
                    "message": f"Check failed: {e}"
                })
        return results
    
    def _check_duplicate_ips(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for actual duplicate IP addresses (same IP used multiple times)."""
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        all_text = " ".join(evidence.to_dict().values())
        ips = re.findall(ip_pattern, all_text)
        
        # Filter out common non-host IPs and subnet masks
        filtered_ips = []
        for ip in ips:
            if ip.startswith(('169.254', '127.', '0.')):
                continue
            # Skip subnet masks
            if ip in ('255.255.255.0', '255.255.255.255', '255.255.0.0', '255.0.0.0'):
                continue
            filtered_ips.append(ip)
        
        from collections import Counter
        ip_counts = Counter(filtered_ips)
        dup_ips = [ip for ip, count in ip_counts.items() if count > 1]
        
        if dup_ips:
            return {
                "check": "duplicate_ips",
                "status": "FAIL",
                "message": f"Duplicate IP addresses detected: {dup_ips}",
                "severity": "HIGH"
            }
        return None
    
    def _check_wrong_subnet_mask(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for common wrong subnet masks."""
        mask_pattern = r'subnet mask[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        all_text = " ".join(evidence.to_dict().values()).lower()
        matches = re.findall(mask_pattern, all_text)
        
        wrong_masks = ['255.255.0.0', '255.0.0.0', '255.255.255.255']
        found_wrong = [m for m in matches if m in wrong_masks]
        
        if found_wrong:
            return {
                "check": "wrong_subnet_mask",
                "status": "FAIL",
                "message": f"Incorrect subnet mask detected: {found_wrong}. Should be 255.255.255.0 for /24 networks",
                "severity": "HIGH"
            }
        return None
    
    def _check_gateway_mismatch(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check if default gateway matches local subnet."""
        all_text = " ".join(evidence.to_dict().values())
        
        # Extract gateway
        gw_match = re.search(r'default gateway[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', all_text, re.IGNORECASE)
        ip_match = re.search(r'ip address[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', all_text, re.IGNORECASE)
        mask_match = re.search(r'subnet mask[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', all_text, re.IGNORECASE)
        
        if gw_match and ip_match and mask_match:
            gateway = gw_match.group(1)
            ip = ip_match.group(1)
            mask = mask_match.group(1)
            
            # Check if gateway is in same subnet
            if not self._same_subnet(ip, gateway, mask):
                return {
                    "check": "gateway_mismatch",
                    "status": "FAIL",
                    "message": f"Default gateway {gateway} not in same subnet as IP {ip}/{mask}",
                    "severity": "HIGH"
                }
        return None
    
    def _check_interface_down(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for administratively down interfaces."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'administratively down' in all_text or 'admin down' in all_text:
            return {
                "check": "interface_down",
                "status": "FAIL",
                "message": "Interface found in 'administratively down' state",
                "severity": "HIGH"
            }
        return None
    
    def _check_missing_vlan(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for missing VLAN configuration."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        vlan_keywords = ['vlan 10', 'vlan 20', 'vlan 30']
        missing = []
        
        for vlan in vlan_keywords:
            if vlan in all_text and ('missing' in all_text or 'not found' in all_text or 'absent' in all_text):
                missing.append(vlan)
        
        if missing:
            return {
                "check": "missing_vlan",
                "status": "FAIL",
                "message": f"Missing VLANs detected: {missing}",
                "severity": "HIGH"
            }
        return None
    
    def _check_missing_route(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for missing routes in routing table."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'show ip route' in all_text:
            if 'no route' in all_text or 'not in routing table' in all_text:
                return {
                    "check": "missing_route",
                    "status": "FAIL",
                    "message": "Destination network not found in routing table",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_pool_missing(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for missing DHCP pool."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in all_text:
            if 'no ip dhcp pool' in all_text or 'pool.*missing' in all_text or 'no pool' in all_text:
                return {
                    "check": "dhcp_pool_missing",
                    "status": "FAIL",
                    "message": "DHCP pool is missing from router configuration",
                    "severity": "HIGH"
                }
            if '169.254' in all_text:
                return {
                    "check": "dhcp_pool_missing",
                    "status": "FAIL",
                    "message": "Client has APIPA address (169.254.x.x) - DHCP pool likely missing",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_wrong_network(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for DHCP pool configured for wrong network."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in all_text and 'network' in all_text:
            # Look for network mismatch patterns
            if 'wrong network' in all_text or 'incorrect network' in all_text:
                return {
                    "check": "dhcp_wrong_network",
                    "status": "FAIL",
                    "message": "DHCP pool configured for incorrect network",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_wrong_gateway(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for DHCP providing wrong default gateway."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in all_text and 'default.router' in all_text or 'default-gateway' in all_text:
            if 'wrong gateway' in all_text or 'incorrect gateway' in all_text:
                return {
                    "check": "dhcp_wrong_gateway",
                    "status": "FAIL",
                    "message": "DHCP pool providing incorrect default gateway",
                    "severity": "HIGH"
                }
        return None
    
    def _check_acl_blocking(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for ACL blocking traffic."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'access-list' in all_text or 'access-group' in all_text:
            if 'deny' in all_text and ('block' in all_text or 'drop' in all_text):
                return {
                    "check": "acl_blocking",
                    "status": "FAIL",
                    "message": "ACL deny rule blocking expected traffic",
                    "severity": "HIGH"
                }
        return None
    
    def _check_nat_missing(self, evidence: Evidence, case: Case) -> Dict[str, Any] | None:
        """Check for missing NAT configuration."""
        all_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'nat' in all_text:
            if 'no ip nat' in all_text or 'nat missing' in all_text or 'not translated' in all_text:
                return {
                    "check": "nat_missing",
                    "status": "FAIL",
                    "message": "NAT configuration missing or incomplete",
                    "severity": "HIGH"
                }
        return None
    
    def _same_subnet(self, ip1: str, ip2: str, mask: str) -> bool:
        """Check if two IPs are in same subnet."""
        ip1_parts = list(map(int, ip1.split('.')))
        ip2_parts = list(map(int, ip2.split('.')))
        mask_parts = list(map(int, mask.split('.')))
        
        for i in range(4):
            if (ip1_parts[i] & mask_parts[i]) != (ip2_parts[i] & mask_parts[i]):
                return False
        return True


def run_rule_checker(evidence: Evidence, case: Case = None) -> List[Dict[str, Any]]:
    """Convenience function to run rule checker."""
    checker = RuleChecker()
    return checker.run_all_checks(evidence, case)