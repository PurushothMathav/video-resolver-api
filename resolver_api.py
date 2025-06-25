from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os
import traceback
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


app = Flask(__name__)
CORS(app)  # Allow requests from any origin (or restrict to GitHub pages if needed)

@app.route('/resolve')
def resolve():
    source_url = request.args.get('url')
    if not source_url:
        return jsonify({'error': 'Missing URL'}), 400

    headers = {
        "Referer": "https://www.5movierulz.tax/",
        "User-Agent": "Mozilla/5.0"
    }

    session = requests.Session()
    try:
        r = session.get(source_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find uperbox.net link
        uperbox_url = next((a['href'].strip() for a in soup.find_all("a", href=True) if "uperbox.net" in a['href']), None)
        if not uperbox_url:
            return jsonify({'error': 'No UperBox link found'}), 404

        # Get tokenized download link
        r2 = session.get(uperbox_url, headers=headers, verify=False)
        match = re.search(r'href="(/[^"]*download\?token=[^"]+)"', r2.text)
        if not match:
            return jsonify({'error': 'No tokenized download link found'}), 404

        download_url = "https://www.uperbox.net" + match.group(1)
        r3 = session.get(download_url, headers=headers2, allow_redirects=False, verify=False)
        final_url = r3.headers.get("Location")

        if final_url:
            return jsonify({'video': final_url})
        else:
            return jsonify({'error': 'Failed to resolve final redirect'}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
