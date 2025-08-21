#!/usr/bin/env python3
"""
Command-line interface for Enhanced Patent Search Agent
Usage: python patent_cli.py [command] [options]
"""

import argparse
import json
import sys
from pathlib import Path
from enhanced_patent_agent import EnhancedPatentAgent, create_agent

def search_keywords(args):
    """Search patents by keywords"""
    agent = create_agent()
    
    params = {
        'search_type': 'keywords',
        'keywords': args.keywords,
        'max_results': args.max_results,
        'include_pdfs': args.download_pdfs
    }
    
    print(f"🔍 Searching for: {' '.join(args.keywords)}")
    results = agent.search_patents(params)
    
    print(f"\n📊 Found {results['total_results']} patents")
    print(f"Download directory: {results['download_dir']}")
    
    for i, patent in enumerate(results['patents'], 1):
        print(f"\n{i}. {patent.get('title', 'No title')[:80]}...")
        print(f"   Patent: {patent.get('patent_number', 'N/A')}")
        print(f"   Date: {patent.get('publication_date', 'N/A')}")
        
        if 'download_result' in patent:
            dr = patent['download_result']
            if dr.success:
                print(f"   ✅ PDF: {Path(dr.file_path).name}")
            else:
                print(f"   ❌ PDF failed: {dr.error_message}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {args.output}")

def lookup_patent(args):
    """Look up specific patent by number"""
    agent = create_agent()
    
    params = {
        'search_type': 'patent_number',
        'patent_number': args.patent_number,
        'include_pdf': args.download_pdf
    }
    
    print(f"🔍 Looking up patent: {args.patent_number}")
    result = agent.search_patents(params)
    
    if result['patent_data']:
        patent = result['patent_data']
        print(f"\n📄 {patent.get('title', 'No title')}")
        print(f"Patent Number: {patent.get('patent_number', 'N/A')}")
        print(f"Publication Date: {patent.get('publication_date', 'N/A')}")
        print(f"Filing Date: {patent.get('filing_date', 'N/A')}")
        print(f"Inventors: {', '.join(patent.get('inventors', []))}")
        print(f"Assignees: {', '.join(patent.get('assignees', []))}")
        
        if patent.get('abstract'):
            print(f"\nAbstract: {patent['abstract'][:300]}...")
        
        if 'download_result' in patent:
            dr = patent['download_result']
            if dr.success:
                print(f"\n✅ PDF downloaded: {dr.file_path}")
                print(f"File size: {dr.file_size / 1024:.1f} KB")
            else:
                print(f"\n❌ PDF download failed: {dr.error_message}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {args.output}")
    else:
        print("❌ Patent not found")

def search_inventor(args):
    """Search patents by inventor"""
    agent = create_agent()
    
    params = {
        'search_type': 'inventor',
        'inventor_name': args.inventor_name,
        'max_results': args.max_results
    }
    
    print(f"🔍 Searching patents by inventor: {args.inventor_name}")
    results = agent.search_patents(params)
    
    print(f"\n📊 Found patents by {args.inventor_name}")
    for i, patent in enumerate(results, 1):
        print(f"{i}. {patent.get('title', 'No title')[:60]}...")
        print(f"   Patent: {patent.get('patent_number', 'N/A')}")

def search_assignee(args):
    """Search patents by assignee/company"""
    agent = create_agent()
    
    params = {
        'search_type': 'assignee',
        'assignee_name': args.assignee_name,
        'max_results': args.max_results
    }
    
    print(f"🔍 Searching patents by assignee: {args.assignee_name}")
    results = agent.search_patents(params)
    
    print(f"\n📊 Found patents by {args.assignee_name}")
    for i, patent in enumerate(results, 1):
        print(f"{i}. {patent.get('title', 'No title')[:60]}...")
        print(f"   Patent: {patent.get('patent_number', 'N/A')}")

def search_chemical(args):
    """Search chemical compound patents"""
    agent = create_agent()
    
    params = {
        'search_type': 'chemical',
        'compound_name': args.compound_name,
        'smiles': getattr(args, 'smiles', ''),
        'molecular_formula': getattr(args, 'molecular_formula', ''),
        'max_results': args.max_results
    }
    
    print(f"🔍 Searching chemical patents for: {args.compound_name}")
    results = agent.search_patents(params)
    
    print(f"\n📊 Found chemical patents")
    for i, patent in enumerate(results.get('results', []), 1):
        print(f"{i}. {patent.get('title', 'No title')[:60]}...")
        print(f"   Patent: {patent.get('patent_number', 'N/A')}")

def show_status(args):
    """Show download status"""
    agent = create_agent()
    status = agent.get_download_status()
    
    print("📊 Patent Download Status")
    print("=" * 40)
    print(f"Download Directory: {status['download_directory']}")
    print(f"Total PDFs: {status['total_pdfs']}")
    print(f"Total Size: {status['total_size_mb']} MB")
    
    if status['files']:
        print(f"\n📄 Recent files:")
        for file_info in status['files'][:10]:
            print(f"  • {file_info['name']} ({file_info['size_kb']} KB)")
    else:
        print("\nNo PDF files found")

def cleanup(args):
    """Clean up old downloaded files"""
    agent = create_agent()
    
    days = getattr(args, 'days', 30)
    result = agent.cleanup_downloads(days)
    
    print(f"🧹 Cleanup complete:")
    print(f"Removed {result['removed_files']} files")
    print(f"Freed {result['size_freed_mb']} MB of space")
    
    if result['files_removed']:
        print("\nRemoved files:")
        for filename in result['files_removed']:
            print(f"  • {filename}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Patent Search Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by keywords
  python patent_cli.py search-keywords "FOXP2" "autism" --max-results 20 --download-pdfs
  
  # Look up specific patent
  python patent_cli.py lookup-patent US10123456B2 --download-pdf
  
  # Search by inventor
  python patent_cli.py search-inventor "John Smith" --max-results 10
  
  # Search by company
  python patent_cli.py search-assignee "Google Inc" --max-results 15
  
  # Search chemical compounds
  python patent_cli.py search-chemical "caffeine" --max-results 10
  
  # Check download status
  python patent_cli.py status
  
  # Clean up old files
  python patent_cli.py cleanup --days 30
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search keywords command
    search_parser = subparsers.add_parser('search-keywords', help='Search patents by keywords')
    search_parser.add_argument('keywords', nargs='+', help='Keywords to search for')
    search_parser.add_argument('--max-results', type=int, default=20, help='Maximum results (default: 20)')
    search_parser.add_argument('--download-pdfs', action='store_true', help='Download PDF files')
    search_parser.add_argument('--output', help='Save results to JSON file')
    search_parser.set_defaults(func=search_keywords)
    
    # Lookup patent command
    lookup_parser = subparsers.add_parser('lookup-patent', help='Look up specific patent')
    lookup_parser.add_argument('patent_number', help='Patent number (e.g., US10123456B2)')
    lookup_parser.add_argument('--download-pdf', action='store_true', help='Download PDF file')
    lookup_parser.add_argument('--output', help='Save results to JSON file')
    lookup_parser.set_defaults(func=lookup_patent)
    
    # Search inventor command
    inventor_parser = subparsers.add_parser('search-inventor', help='Search patents by inventor')
    inventor_parser.add_argument('inventor_name', help='Inventor name')
    inventor_parser.add_argument('--max-results', type=int, default=20, help='Maximum results')
    inventor_parser.set_defaults(func=search_inventor)
    
    # Search assignee command
    assignee_parser = subparsers.add_parser('search-assignee', help='Search patents by assignee')
    assignee_parser.add_argument('assignee_name', help='Company/assignee name')
    assignee_parser.add_argument('--max-results', type=int, default=20, help='Maximum results')
    assignee_parser.set_defaults(func=search_assignee)
    
    # Search chemical command
    chemical_parser = subparsers.add_parser('search-chemical', help='Search chemical patents')
    chemical_parser.add_argument('compound_name', help='Chemical compound name')
    chemical_parser.add_argument('--smiles', help='SMILES notation')
    chemical_parser.add_argument('--molecular-formula', help='Molecular formula')
    chemical_parser.add_argument('--max-results', type=int, default=20, help='Maximum results')
    chemical_parser.set_defaults(func=search_chemical)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show download status')
    status_parser.set_defaults(func=show_status)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old downloads')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Remove files older than N days')
    cleanup_parser.set_defaults(func=cleanup)
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.set_defaults(func=lambda args: __import__('enhanced_patent_agent').interactive_search())
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()