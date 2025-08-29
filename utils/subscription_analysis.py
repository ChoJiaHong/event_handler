def analyze_subscription_info(subscription_info: dict) -> dict:
    """
    分析訂閱資訊內容，統計各項指標。
    
    回傳結果內容包括:
      - total_agents: agents 總數
      - service_stats: 各服務類型數量
      - node_stats: 各節點數量
      - port_stats: 各端口數量
    """
    raw_agents = subscription_info.get("raw", [])
    analysis = {
        "total_agents": len(raw_agents),
        "service_stats": {},
        "node_stats": {},
        "port_stats": {}
    }
    
    for agent in raw_agents:
        service_type = agent.get("serviceType", "unknown")
        analysis["service_stats"][service_type] = analysis["service_stats"].get(service_type, 0) + 1
        
        node_name = agent.get("nodeName", "unknown")
        analysis["node_stats"][node_name] = analysis["node_stats"].get(node_name, 0) + 1
        
        port = agent.get("agentPort", 0)
        analysis["port_stats"][port] = analysis["port_stats"].get(port, 0) + 1
    return analysis
def get_service_stats_str(service_stats: dict) -> str:
    lines = ["\n🔍 服務類型分布:"]
    for service_type, count in service_stats.items():
        lines.append(f"  {service_type}: {count} agents")
    return "\n".join(lines)

def get_node_stats_str(node_stats: dict) -> str:
    lines = ["\n🖥️  節點分布:"]
    for node_name, count in node_stats.items():
        lines.append(f"  {node_name}: {count} agents")
    return "\n".join(lines)

def get_port_stats_str(port_stats: dict) -> str:
    lines = ["\n🔌 端口分布:"]
    for port, count in sorted(port_stats.items()):
        lines.append(f"  {port}: {count} agents")
    return "\n".join(lines)

def get_agents_detail_str(raw_agents: list, top_n: int = 5) -> str:
    lines = [f"\n📋 前 {top_n} 個 agents 詳細資訊:"]
    for i, agent in enumerate(raw_agents[:top_n]):
        lines.append(f"  Agent {i+1}:")
        lines.append(f"    IP: {agent.get('agentIP', 'N/A')}")
        lines.append(f"    Port: {agent.get('agentPort', 'N/A')}")
        lines.append(f"    Service: {agent.get('serviceType', 'N/A')}")
        lines.append(f"    Node: {agent.get('nodeName', 'N/A')}")
        lines.append(f"    Pod IP: {agent.get('podIP', 'N/A')}")
        lines.append("")
    return "\n".join(lines)

def get_subscription_analysis_str(analysis: dict, raw_agents: list, top_n: int = 5) -> str:
    """
    回傳訂閱資訊分析結果與前 N 筆 agents 的詳細資訊字串。
    """
    result = [
        "📊 訂閱資料分析:",
        f"總 agents 數量: {analysis.get('total_agents', 0)}",
        get_service_stats_str(analysis.get("service_stats", {})),
        get_node_stats_str(analysis.get("node_stats", {})),
        get_port_stats_str(analysis.get("port_stats", {})),
        get_agents_detail_str(raw_agents, top_n)
    ]
    return "\n".join(result)