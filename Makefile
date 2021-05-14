reports/Proposal.pdf : reports/Proposal.md reports/images/TimelineGanttChart.pdf
	pandoc reports/Proposal.md -o reports/Proposal.pdf

clean :
	rm -f reports/Proposal.pdf