with open("alcli/version.py", "r") as f:
     exec(f.read())
with open("build_version", "w") as f:
    print(version)
    f.write(version)

