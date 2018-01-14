import json
import sys
import worker.api as worker

if __name__ == '__main__':
    # query = sys.argv[1] if len(sys.argv) > 1 else 'Санкт'
    
    query = input('Please enter a city: ')
    result = worker.main_page(query if len(query) > 0 else 'Санкт')
    
    # out = sys.argv[2] if len(sys.argv) > 2 else 'output.json'
    
    out = input('Please enter output filename: ')
    out = open(out if len(out) > 0 else 'output.json', 'w')
    
    json.dump(result, out, indent = 4)
    print('Done')
