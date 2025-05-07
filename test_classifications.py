import asyncio
import json
from ergo_explorer.tools.address import get_common_interactions

async def main():
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    result = await get_common_interactions(address, limit=3)
    
    print('All addresses with classifications:')
    for i, addr in enumerate(result['common_interactions']):
        print(f"{i+1}. {addr['formatted_address']}:")
        print(f"   Classifications: {json.dumps({k: v for k, v in addr.items() if k.startswith('is_')}, indent=2)}")
        print(f"   Confidence scores: {json.dumps(addr['confidence_scores'], indent=2)}")
        print()
    
    # Print summary stats
    print("Classification summary:")
    dex_count = sum(1 for addr in result['common_interactions'] if addr.get('is_dex', False))
    contract_count = sum(1 for addr in result['common_interactions'] if addr.get('is_smartcontract', False))
    p2p_count = sum(1 for addr in result['common_interactions'] if addr.get('is_p2p', False))
    recurring_count = sum(1 for addr in result['common_interactions'] if addr.get('is_recurring', False))
    
    total = len(result['common_interactions'])
    print(f"DEX: {dex_count}/{total} ({dex_count/total*100:.1f}%)")
    print(f"Smart Contracts: {contract_count}/{total} ({contract_count/total*100:.1f}%)")
    print(f"P2P: {p2p_count}/{total} ({p2p_count/total*100:.1f}%)")
    print(f"Recurring: {recurring_count}/{total} ({recurring_count/total*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main()) 