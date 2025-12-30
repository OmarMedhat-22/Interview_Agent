import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 120  # seconds
RESULTS_FILE = None  # Set to filename to save results

# Available models (name -> full model string)
MODELS = {
    # Gemini models
    "gemini-2.5-flash": "gemini/gemini-2.5-flash",
    "gemini-2.5-pro": "gemini/gemini-2.5-pro",
    "gemini-2.0-flash": "gemini/gemini-2.0-flash",
    "gemini-lite": "gemini/gemini-2.0-flash-lite",
    # Claude models
    "claude-4": "claude-sonnet-4-20250514",
    "claude-3.5": "claude-3-5-sonnet-20241022",
    "claude-haiku": "claude-3-haiku-20240307",
}

# API Keys - Load from environment variables or set here
import os
API_KEYS = {
    "gemini1": os.getenv("GEMINI_API_KEY", ""),
    "gemini2": os.getenv("GEMINI_API_KEY_2", ""),
    "claude": os.getenv("ANTHROPIC_API_KEY", ""),
}

# Current settings
CURRENT_MODEL = None  # None = use server default
CURRENT_API_KEY = None  # None = use server default


def set_model(model_name):
    """Set model by name"""
    global CURRENT_MODEL
    if model_name in MODELS:
        CURRENT_MODEL = MODELS[model_name]
    else:
        CURRENT_MODEL = model_name
    print(f"Model set to: {CURRENT_MODEL}")


def set_api_key(key_name):
    """Set API key by name (key1, key2, etc.)"""
    global CURRENT_API_KEY
    CURRENT_API_KEY = API_KEYS.get(key_name, key_name)
    print(f"API key set to: {key_name}")


def set_output_file(filename=None):
    """Set output file for results"""
    global RESULTS_FILE
    if filename is None:
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    RESULTS_FILE = filename
    print(f"Results will be saved to: {RESULTS_FILE}")


def save_result(result_data):
    """Save result to file"""
    if not RESULTS_FILE:
        return
    
    try:
        # Load existing results or create new
        try:
            with open(RESULTS_FILE, 'r') as f:
                all_results = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_results = {"timestamp": datetime.now().isoformat(), "results": []}
        
        all_results["results"].append(result_data)
        
        with open(RESULTS_FILE, 'w') as f:
            json.dump(all_results, f, indent=2)
    except Exception as e:
        print(f"Error saving result: {e}")


def list_options():
    """List available models and API keys"""
    print("\n=== Available Models ===")
    for name, full in MODELS.items():
        print(f"  {name:20} -> {full}")
    print("\n=== Available API Keys ===")
    for k in API_KEYS.keys():
        print(f"  {k}")
    print(f"\nCurrent model: {CURRENT_MODEL or 'default'}")
    print(f"Current API key: {'custom' if CURRENT_API_KEY else 'default'}")
    print(f"Output file: {RESULTS_FILE or 'none (console only)'}")


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())


TEST_CASES = [
    {
        "question": "Tell me about yourself",
        "answer": "I am a software engineer with 5 years of experience in Python and JavaScript. I have led teams of 3-5 developers and delivered multiple successful projects including a payment processing system that handled 10,000 transactions daily.",
        "job_description": "Senior Software Engineer with Python experience"
    },
    {
        "question": "What is your greatest weakness?",
        "answer": "I sometimes take on too much work because I want to help everyone. I've learned to manage this by using project management tools and setting clear boundaries about my capacity.",
        "job_description": "Project Manager"
    },
    {
        "question": "Why do you want to work here?",
        "answer": "I like your company.",
        "job_description": "Marketing Specialist at Tech Startup"
    },
    {
        "question": "Describe a challenging project you worked on",
        "answer": "I led the migration of our monolithic application to microservices architecture. It took 8 months, involved coordinating with 4 teams, and reduced deployment time from 2 hours to 15 minutes. We also achieved 99.9% uptime during the transition.",
        "job_description": "Software Architect"
    },
    {
        "question": "How do you handle conflict with coworkers?",
        "answer": "I avoid conflict at all costs and just agree with whatever others say to keep the peace.",
        "job_description": "Team Lead"
    },
    {
        "question": "Where do you see yourself in 5 years?",
        "answer": "I see myself growing into a technical leadership role where I can mentor junior developers while still contributing to architecture decisions. I want to help build scalable systems and foster a culture of engineering excellence.",
        "job_description": "Senior Backend Developer"
    },
    {
        "question": "Tell me about a time you failed",
        "answer": "I've never really failed at anything important.",
        "job_description": "Product Manager"
    },
    {
        "question": "How do you stay updated with new technologies?",
        "answer": "I dedicate 5 hours weekly to learning. I follow tech blogs like Martin Fowler and ThoughtWorks, contribute to open source projects, attend local meetups monthly, and recently completed AWS Solutions Architect certification.",
        "job_description": "DevOps Engineer"
    },
    {
        "question": "Why are you leaving your current job?",
        "answer": "My current company has limited growth opportunities. I've mastered my current role and am seeking challenges that align with my career goals in machine learning, which your company specializes in.",
        "job_description": "Machine Learning Engineer"
    },
    {
        "question": "What salary are you expecting?",
        "answer": "Based on my 7 years of experience, market research, and the scope of this role, I'm targeting $130,000-$150,000. However, I'm open to discussing the complete compensation package including benefits and growth opportunities.",
        "job_description": "Engineering Manager"
    }
]


def test_evaluate(test_index=None):
    if test_index is not None:
        cases = [(test_index, TEST_CASES[test_index])]
    else:
        cases = list(enumerate(TEST_CASES))
    
    for i, test_case in cases:
        payload = test_case.copy()
        
        # Add model and API key if set
        if CURRENT_MODEL:
            payload["model"] = CURRENT_MODEL
        if CURRENT_API_KEY:
            payload["api_key"] = CURRENT_API_KEY
        
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: {payload['question']}")
        print(f"{'='*60}")
        print(f"Answer: {payload['answer'][:100]}...")
        print(f"Job: {payload['job_description']}")
        if CURRENT_MODEL:
            print(f"Model: {CURRENT_MODEL}")
        
        print("\nEvaluating...")
        response = requests.post(f"{BASE_URL}/evaluate", json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nScore: {result['score']}/100")
            print(f"Summary: {result['summary']}")
            print(f"\nCriteria: relevance={result['criteria_breakdown']['relevance']}, "
                  f"clarity={result['criteria_breakdown']['clarity']}, "
                  f"depth={result['criteria_breakdown']['depth']}, "
                  f"impact={result['criteria_breakdown']['impact']}, "
                  f"job_alignment={result['criteria_breakdown']['job_alignment']}")
            print(f"\nStrengths: {', '.join(result['strengths'][:2])}")
            print(f"Weaknesses: {', '.join(result['weaknesses'][:2])}")
            
            # Save to file if enabled
            save_result({
                "test_index": i,
                "question": payload['question'],
                "answer": payload['answer'],
                "job_description": payload['job_description'],
                "model": CURRENT_MODEL or "default",
                "result": result
            })
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:200])
    
    if RESULTS_FILE:
        print(f"\n✓ Results saved to: {RESULTS_FILE}")


def test_single(index):
    """Test a single case by index (0-9)"""
    test_evaluate(index)


def interactive_menu():
    """Interactive menu for testing"""
    while True:
        print("\n" + "="*60)
        print("Interview Agent Test Menu")
        print("="*60)
        print("1. Run all tests")
        print("2. Run single test (0-9)")
        print("3. Change model")
        print("4. Change API key")
        print("5. Set output file")
        print("6. Show current settings")
        print("7. Health check")
        print("0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            test_evaluate()
        elif choice == "2":
            idx = input("Test index (0-9): ").strip()
            test_evaluate(int(idx))
        elif choice == "3":
            print("\nAvailable models:")
            for name in MODELS.keys():
                print(f"  {name}")
            name = input("Model name: ").strip()
            set_model(name)
        elif choice == "4":
            print("\nAvailable keys:", list(API_KEYS.keys()))
            key = input("Key name: ").strip()
            set_api_key(key)
        elif choice == "5":
            filename = input("Filename (or press Enter for auto): ").strip()
            set_output_file(filename if filename else None)
        elif choice == "6":
            list_options()
        elif choice == "7":
            test_health()


if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:]
    test_idx = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-i" or arg == "--interactive":
            interactive_menu()
            sys.exit(0)
        elif arg == "-l" or arg == "--list":
            list_options()
            sys.exit(0)
        elif arg == "-m" and i + 1 < len(args):
            set_model(args[i + 1])
            i += 1
        elif arg == "-o" or arg == "--output":
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                set_output_file(args[i + 1])
                i += 1
            else:
                set_output_file()  # Auto-generate filename
        elif arg.isdigit():
            test_idx = int(arg)
        i += 1
    
    if len(args) > 0 and not (args[0] == "-i" or args[0] == "-l"):
        test_health()
        if test_idx is not None:
            test_evaluate(test_idx)
        else:
            test_evaluate()  # Run all tests
    elif len(args) == 0:
        print("Usage:")
        print("  python test_api.py                    - Show help")
        print("  python test_api.py -i                 - Interactive menu")
        print("  python test_api.py -l                 - List models/keys")
        print("  python test_api.py 0                  - Run test 0")
        print("  python test_api.py -m claude-4 0      - Use claude-4, run test 0")
        print("  python test_api.py -o results.json 0  - Save to file, run test 0")
        print("  python test_api.py -o -m claude-4     - Auto filename, all tests")
        print("\nAvailable models:", ", ".join(MODELS.keys()))
