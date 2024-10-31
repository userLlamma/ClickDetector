# scripts/manage_tokens.py
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from deploy.inference.tools.token_management import TokenManagement

def main():
    parser = argparse.ArgumentParser(description='Token Management CLI')
    parser.add_argument('action', choices=['add', 'revoke', 'list', 'check'])
    parser.add_argument('--description', '-d', help='Token description')
    parser.add_argument('--days', type=int, default=30, help='Token validity in days')
    parser.add_argument('--prefix', default='test', help='Token prefix')
    parser.add_argument('--token', help='Token to revoke')
    
    args = parser.parse_args()

    # 获取配置文件路径
    config_path = Path(__file__).parent.parent / "deploy" / "inference" / "config" / "inference_config.yaml"
    manager = TokenManagement(str(config_path))

    if args.action == 'add':
        if not args.description:
            print("Error: Description is required for adding new token")
            return
        token, expires = manager.add_token(
            description=args.description,
            days=args.days,
            prefix=args.prefix
        )
        print(f"Created new token: {token}")
        print(f"Expires at: {expires}")

    elif args.action == 'revoke':
        if not args.token:
            print("Error: Token is required for revocation")
            return
        manager.revoke_token(args.token)
        print(f"Revoked token: {args.token}")

    elif args.action == 'list':
        status = manager.check_token_status()
        print("\nActive tokens:")
        for token in status['active']:
            print(f"- {token['token']} ({token['description']})")
        
        print("\nExpiring soon:")
        for token in status['expiring_soon']:
            print(f"- {token['token']} ({token['description']})")
        
        print("\nExpired tokens:")
        for token in status['expired']:
            print(f"- {token['token']} ({token['description']})")

    elif args.action == 'check':
        if not args.token:
            print("Error: Token is required for checking")
            return
        valid = manager.check_token(args.token)
        print(f"Token {args.token} is {'valid' if valid else 'invalid'}")

if __name__ == '__main__':
    main()