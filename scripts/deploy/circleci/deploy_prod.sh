#!/usr/bin/env bash
# This script deploys the built site to the prod-pages branch of the same repo.

# Customize these variables for your specific implementation.
###################################
# This is the Github organisation or username of your fork. For example, if
# your fork is located at https://github.com/xyz/open-sdg-site-starter, then
# you should put "xyz" here. Changing this is required.
GH_ORG_PROD="CHANGEME"
# These variables only control the name/email on the automated Git commits.
# Changing this is optional.
GH_NAME="CircleCI"
GH_EMAIL="no-reply@example.com"
###################################

# There is probably no need to modify anything below this point.
git config --global user.email "$GH_EMAIL"
git config --global user.name "$GH_NAME"

# CircleCI will identify the SSH key with a "Host" of gh-prod. In order to tell
# Git to use this key, we need to hack the SSH key:
sed -i -e 's/Host gh-prod/Host gh-prod\n  HostName github.com/g' ~/.ssh/config
git clone git@gh-prod:$GH_ORG_PROD/$CIRCLE_PROJECT_REPONAME.git out

cd out
git checkout gh-pages || git checkout --orphan gh-pages
git rm -rfq .
cd ..

# The fully built site is already available at /tmp/build.
cp -a /tmp/build/_site/. out/.

mkdir -p out/.circleci && cp -a .circleci/. out/.circleci/.
cd out

git add -A
git commit -m "Automated deployment to GitHub Pages: ${CIRCLE_SHA1}" --allow-empty

git push origin gh-pages