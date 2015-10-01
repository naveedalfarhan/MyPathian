#!/bin/sh
cat << EOF > .git/hooks/pre-commit
#!/bin/sh

if [[ \$(git diff --name-only --cached | grep "requirements-pinned.txt") ]]; then
    echo "Modify requirements.txt instead of requirements-pinned.txt";
    exit 1;
fi

status_commits=\$(git status --porcelain | grep -v \?\? | wc -l)

if [ \$status_commits != "0" ]; then
	git stash -q --keep-index
fi

# in case someone edited requirements.txt without actually installing the package yet
echo "Installing latest requirements from requirements.txt"
env/Scripts/pip install -q -r requirements.txt

echo "Pinning dependencies to requirements-pinned.txt"
env/Scripts/pip freeze -r requirements.txt > requirements-pinned.txt

git add requirements.txt requirements-pinned.txt

if [ \$status_commits != "0" ]; then
	git stash pop -q
fi
EOF

cat << EOF > .git/hooks/post-merge
#!/bin/bash
echo "Updating requirements from requirements-pinned.txt"
env/Scripts/pip install -r requirements-pinned.txt
EOF


cat << EOF > .git/hooks/post-checkout
#!/bin/bash
echo "Updating requirements from requirements-pinned.txt"
env/Scripts/pip install -r requirements-pinned.txt
EOF