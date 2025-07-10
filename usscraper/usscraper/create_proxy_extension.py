import zipfile
import os

proxy_host = "unblock.oxylabs.io"
proxy_port = 60000
proxy_user = "deepdive_0TdFW"
proxy_pass = "i_NhRAuyg4uRM_J"

manifest_json = """
{
  "version": "1.0.0",
  "manifest_version": 2,
  "name": "Chrome Proxy",
  "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
  "background": {
    "scripts": ["background.js"]
  },
  "minimum_chrome_version":"22.0.0"
}
"""

background_js = f"""
var config = {{
  mode: "fixed_servers",
  rules: {{
    singleProxy: {{
      scheme: "http",
      host: "{proxy_host}",
      port: parseInt({proxy_port})
    }},
    bypassList: ["localhost"]
  }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

chrome.webRequest.onAuthRequired.addListener(
  function(details) {{
    return {{
      authCredentials: {{
        username: "{proxy_user}",
        password: "{proxy_pass}"
      }}
    }};
  }},
  {{urls: ["<all_urls>"]}},
  ['blocking']
);
"""

with zipfile.ZipFile("proxy_auth_plugin.zip", "w") as zipf:
    zipf.writestr("manifest.json", manifest_json)
    zipf.writestr("background.js", background_js)
