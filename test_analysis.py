import requests

def test_analysis():
    url = "http://localhost:8000/resume/analyze-match"
    files = {'file': ('resume.pdf', b'fake pdf content with react', 'application/pdf')}
    data = {'job_description': 'Looking for a React developer'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_analysis()
