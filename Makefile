reports/Proposal.pdf : reports/Proposal.Rmd reports/images/TimelineGanttChart.pdf data/927
	Rscript -e "rmarkdown::render('reports/Proposal.Rmd',output_file='Proposal.pdf')"

clean :
	rm -f reports/Proposal.pdf