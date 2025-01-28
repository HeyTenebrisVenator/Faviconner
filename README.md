# Faviconner
faviconner is a python tool that allow you to discover the favicon hash from multiple domains/subdomains

This tool is specially made for bug bounter or pentester that want to improve their recon methodology.

To use reconner you need first install the requirements.txt

```sudo pip install -r requirements.txt```

*WHAT TO DO WITH THE HASH?*

The favicon hash can be used for many recon processes, as use it in censys or shodan

SHODAN:
```http.favicon.hash:<hash>```

CENSYS:
```services.http.response.favicons.hashes:<hash>```

