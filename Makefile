workflow:
	kojo file ../workflow-templates/workflows/python-lib/deploy.yml -s .github/workflows/deploy.yml
	kojo file ../workflow-templates/workflows/python-lib/pr.yml -s .github/workflows/pr.yml black=true
	kojo file ../workflow-templates/workflows/shared/create-release.yml -s .github/workflows/create-release.yml
