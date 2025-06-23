# diglet

**diglet** is a flexible, scriptable DNS query tool built in Python.  
It resolves a list of domains using a custom set of DNS resolvers, supporting any record type you choose.

---

## 🔍 Features

- 🎯 Query any DNS record type (A, AAAA, TXT, MX, CNAME, NS, SOA, etc.)
- 🔁 Rotate resolvers using round-robin or custom strategy
- 📂 Input domain and resolver lists from files
- 🔧 Built for extensibility and scripting
- ❌ No banners, noise, or hardcoded limits

---

## 📦 Requirements

- Python 3.7+
- [`dnspython`](https://github.com/rthalley/dnspython)

Install with:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
python3 diglet.py domains.txt resolvers.txt
```

By default, it queries A, TXT, and MX records. You can easily modify or extend the script to support other types (e.g., CNAME, AAAA, NS).

---

### Example Input

**`domains.txt`**
```
example.com
protonmail.com
duckduckgo.com
```

**`resolvers.txt`**
```
1.1.1.1
8.8.8.8
9.9.9.9
```

---

### Example Output

```
duckduckgo.com
  A   : ['40.114.177.156']
  TXT : ['v=spf1 include:_spf.google.com ~all']
  MX  : ['10 mail.duckduckgo.com.']
```

---

## 📂 File Layout

```
diglet.py             # main script
requirements.txt      # dependencies
README.md             # this file
domains.txt           # input list of domains
resolvers.txt         # input list of DNS resolvers
```

---

## 📌 Extend It

You can customize `diglet` to:
- Accept record types via CLI (`--type`)
- Output results to CSV or JSON
- Run queries concurrently
- Log errors to file
- Integrate into other systems or pipelines

---

## ✅ License

MIT — use, fork, and build on it freely.

---

## 🧠 Why diglet?

Because `dig`, `dnsx`, and `massdns` are great — but **you want control.**
No mystery code, no black-box behavior.  
Just clean DNS queries, built your way.
