reports/Proposal.pdf : reports/Proposal.md
	pandoc reports/Proposal.md -o reports/Proposal.pdf
	
clean :
	rm -f reports/Proposal.pdf