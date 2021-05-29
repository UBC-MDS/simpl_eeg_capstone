all : reports/Proposal.pdf

reports/images/viz_example.png : reports/generate_figures.py data/927/.*
	python reports/generate_figures.py

reports/Proposal.pdf : reports/Proposal.Rmd reports/images/TimelineGanttChart.pdf data/927/.*
	Rscript -e "rmarkdown::render('reports/Proposal.Rmd',output_file='Proposal.pdf')"

ui :
	streamlit run src/app.py

clean :
	rm -f reports/images/viz_example.png
	rm -f reports/Proposal.pdf