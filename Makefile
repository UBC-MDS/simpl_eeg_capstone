IMG_DEPS := reports/images/viz_example.png 
IMG_DEPS += reports/images/raw_voltage.png 
IMG_DEPS += reports/images/2d_head.png
IMG_DEPS += reports/images/3d_head.png
IMG_DEPS += reports/images/3d_brain.png
IMG_DEPS += reports/images/connectivity.png
IMG_DEPS += reports/images/connectivity_circle.png

all : reports/Final_Report.pdf

$(IMG_DEPS) : reports/generate_figures.py data/927/.* simpl_eeg/.*
	python reports/generate_figures.py

reports/Proposal.pdf : reports/Proposal.Rmd reports/images/TimelineGanttChart.pdf data/927/.*
	Rscript -e "rmarkdown::render('reports/Proposal.Rmd', output_file='Proposal.pdf')"

reports/Final_Report.pdf : reports/Final_Report.Rmd $(IMG_DEPS)
	Rscript -e "rmarkdown::render('reports/Final_Report.Rmd', output_file='Final_Report.pdf')"

ui :
	streamlit run src/app.py

install : 
	python -m pip install -e .

test :
	poetry run pytest

clean_docs :
	jb clean docs/simpl_instructions/

build_docs :
	jb build docs/simpl_instructions/

update_docs :
	jb build docs/simpl_instructions/
	ghp-import -n -p -f docs/simpl_instructions/_build/html

clean :
	rm -f reports/images/viz_example.png
	rm -f reports/Proposal.pdf