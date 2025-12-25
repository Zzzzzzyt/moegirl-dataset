PYTHON := $(if $(PYTHON),$(PYTHON),python3)

PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
export PYTHONPATH = $(PROJECT_ROOT)

.PHONY: clean_all
clean:
	@read -p "Are you sure? [y/N] " ans && ans=$${ans:-N} ; \
	if [ $${ans} = y ] || [ $${ans} = Y ]; then \
		printf $(_SUCCESS) "YES" ; \
	else \
		printf $(_DANGER) "NO" ; \
	fi
	rm -rf moegirl/crawler/attrs.json
	rm -rf moegirl/crawler/subjects.json
# 	rm -rf bangumi/bgm_images_medium_mapped.json

	rm -rf moegirl/preprocess/attr_index.json
	rm -rf moegirl/preprocess/attr2char.json
	rm -rf moegirl/preprocess/attr2article.json
	rm -rf moegirl/preprocess/char_index.json
	rm -rf moegirl/preprocess/char2attr.json
	rm -rf moegirl/preprocess/char2cv.json
	rm -rf moegirl/preprocess/cv_index.json
	rm -rf moegirl/preprocess/cv2char.json 
	rm -rf moegirl/preprocess/char2subject.json
	rm -rf moegirl/preprocess/subject_index.json
	rm -rf moegirl/preprocess/fundamental_attr.json
	rm -rf moegirl/crawler_extra/extra_processed.json
	rm -rf moegirl/subset/subset/*
	rm -rf moegirl/analyze/*.npy
	rm -rf moegirl/analyze/gender.json
	rm -rf moegirl/moeranker/data_min.json
	rm -rf moegirl/moeranker/importance.json

	rm -rf bangumi/dump_converter/*.zip
	rm -rf bangumi/dump_converter/*.jsonlines
	rm -rf bangumi/bgm_chars_full.json
	rm -rf bangumi/bgm_index_full.json
	rm -rf bangumi/bgm_redirects_full.json
	rm -rf bangumi/bgm_subjects_full.json
	rm -rf bangumi/moegirl2bgm.json
	rm -rf bangumi/bgm2moegirl.json
	rm -rf bangumi/bgm_info.json
	rm -rf bangumi/subset/subset/*
	rm -rf bangumi/anime_character_guessr/id_tags.js
	rm -rf bangumi/anime_character_guessr/id_tags.json

.PHONY: clean
clean_generated: 
	@read -p "Are you sure? [y/N] " ans && ans=$${ans:-N} ; \
	if [ $${ans} = y ] || [ $${ans} = Y ]; then \
		printf $(_SUCCESS) "YES" ; \
	else \
		printf $(_DANGER) "NO" ; \
	fi
	rm -rf moegirl/preprocess/attr_index.json
	rm -rf moegirl/preprocess/attr2char.json
	rm -rf moegirl/preprocess/attr2article.json
	rm -rf moegirl/preprocess/char_index.json
	rm -rf moegirl/preprocess/char2attr.json
	rm -rf moegirl/preprocess/char2cv.json
	rm -rf moegirl/preprocess/cv_index.json
	rm -rf moegirl/preprocess/cv2char.json 
	rm -rf moegirl/preprocess/char2subject.json
	rm -rf moegirl/preprocess/subject_index.json
	rm -rf moegirl/preprocess/fundamental_attr.json
	rm -rf moegirl/crawler_extra/extra_processed.json
	rm -rf moegirl/subset/subset/*
	rm -rf moegirl/analyze/*.npy
	rm -rf moegirl/analyze/gender.json
	rm -rf moegirl/moeranker/data_min.json
	rm -rf moegirl/moeranker/importance.json

	rm -rf bangumi/dump_converter/*.zip
	rm -rf bangumi/dump_converter/*.jsonlines
	rm -rf bangumi/bgm_chars_full.json
	rm -rf bangumi/bgm_index_full.json
	rm -rf bangumi/bgm_redirects_full.json
	rm -rf bangumi/bgm_subjects_full.json
	rm -rf bangumi/moegirl2bgm.json
	rm -rf bangumi/bgm2moegirl.json
	rm -rf bangumi/bgm_info.json
	rm -rf bangumi/subset/subset/*
	rm -rf bangumi/anime_character_guessr/id_tags.js
	rm -rf bangumi/anime_character_guessr/id_tags.json

.PHONY: all
all: moegirl/crawler/attrs.json moegirl/crawler/subjects.json moegirl/preprocess/attr_index.json moegirl/preprocess/attr2char.json moegirl/preprocess/attr2article.json moegirl/preprocess/char_index.json moegirl/preprocess/char2attr.json moegirl/preprocess/char2cv.json moegirl/preprocess/cv_index.json moegirl/preprocess/cv2char.json  moegirl/preprocess/char2subject.json moegirl/preprocess/subject_index.json moegirl/preprocess/fundamental_attr.json moegirl/crawler_extra/extra_processed.json moegirl/subsets moegirl/analyze/intersection.npy moegirl/analyze/cross.npy moegirl/analyze/count.npy moegirl/analyze/contain.npy moegirl/analyze/gain.npy moegirl/analyze/chi2.npy moegirl/analyze/gender.json moegirl/moeranker/data_min.json moegirl/moeranker/importance.json bangumi/bgm_chars_full.json bangumi/bgm_index_full.json bangumi/bgm_redirects_full.json bangumi/bgm_subjects_full.json bangumi/moegirl2bgm.json bangumi/bgm2moegirl.json bangumi/bgm_info.json bangumi/subsets bangumi/anime_character_guessr/id_tags.js bangumi/anime_character_guessr/id_tags.json

moegirl/crawler/attrs.json moegirl/crawler/subjects.json &:
	$(PYTHON) moegirl/crawler/crawler.py

moegirl/preprocess/attr_index.json moegirl/preprocess/attr2char.json moegirl/preprocess/attr2article.json moegirl/preprocess/char_index.json moegirl/preprocess/char2attr.json moegirl/preprocess/char2cv.json moegirl/preprocess/cv_index.json moegirl/preprocess/cv2char.json &:
	$(PYTHON) moegirl/preprocess/flattener.py

moegirl/preprocess/char2subject.json moegirl/preprocess/subject_index.json &: moegirl/crawler/subjects.json moegirl/preprocess/char_index.json
	$(PYTHON) moegirl/preprocess/flattener2.py

moegirl/preprocess/fundamental_attr.json: moegirl/preprocess/attr_index.json moegirl/crawler/attrs.json moegirl/preprocess/attr2char.json moegirl/preprocess/hair_color_attr.json moegirl/preprocess/eye_color_attr.json
	$(PYTHON) moegirl/preprocess/attr_filter.py


moegirl/crawler_extra/extra_info.json: moegirl/preprocess/char_index.json
	$(PYTHON) moegirl/crawler_extra/crawler_extra.py

moegirl/crawler_extra/extra_processed.json: moegirl/crawler_extra/extra_info.json
	$(PYTHON) moegirl/crawler_extra/process.py


.PHONY: moegirl/subsets
moegirl/subsets: moegirl/crawler/attrs.json moegirl/preprocess/char2subject.json moegirl/preprocess/char_index.json
	$(PYTHON) moegirl/subset/subsetter.py


moegirl/analyze/intersection.npy moegirl/analyze/cross.npy moegirl/analyze/count.npy &: moegirl/preprocess/attr2char.json moegirl/preprocess/char_index.json moegirl/preprocess/attr_index.json
	$(PYTHON) moegirl/analyze/intersection.py

moegirl/analyze/contain.npy moegirl/analyze/gain.npy moegirl/analyze/chi2.npy &: moegirl/analyze/intersection.npy moegirl/preprocess/char_index.json moegirl/preprocess/attr_index.json
	$(PYTHON) moegirl/analyze/correlation.py

moegirl/analyze/gender.json &: moegirl/preprocess/male_attr.json moegirl/preprocess/female_attr.json moegirl/preprocess/nogender_attr.json moegirl/preprocess/char2attr.json bangumi/moegirl2bgm.json bangumi/bgm_chars_full.json
	$(PYTHON) moegirl/analyze/guess_gender.py


moegirl/moeranker/data_min.json &: moegirl/preprocess/char_index.json moegirl/preprocess/attr_index.json moegirl/preprocess/attr2char.json moegirl/preprocess/char2attr.json moegirl/preprocess/attr2article.json moegirl/analyze/gender.json
	$(PYTHON) moegirl/moeranker/minifier.py

moegirl/moeranker/importance.json &: moegirl/preprocess/attr_index.json moegirl/preprocess/char_index.json moegirl/analyze/gain.npy moegirl/analyze/count.npy moegirl/analyze/contain.npy moegirl/analyze/intersection.npy moegirl/preprocess/hair_color_attr.json moegirl/preprocess/eye_color_attr.json
	$(PYTHON) moegirl/moeranker/importance.py

.PHONY: moeranker
moeranker: moegirl/moeranker/data_min.json moegirl/moeranker/importance.json bangumi/moegirl2bgm.json bangumi/bgm_info.json moegirl/subsets bangumi/subsets


bangumi/bgm_chars_full.json bangumi/bgm_index_full.json bangumi/bgm_redirects_full.json bangumi/bgm_subjects_full.json &: 
	$(PYTHON) bangumi/dump_converter/dump_downloader.py
	$(PYTHON) bangumi/dump_converter/dump_converter.py
	$(PYTHON) bangumi/dump_converter/redirect_checker.py
	rm -rf bangumi/dump_converter/*.jsonlines


bangumi/moegirl2bgm.json bangumi/bgm2moegirl.json bangumi/bgm_info.json &: bangumi/bgm_index_full.json bangumi/bgm_chars_full.json bangumi/bgm_subjects_full.json moegirl/preprocess/char_index.json moegirl/crawler_extra/extra_processed.json moegirl/preprocess/char2subject.json
	$(PYTHON) bangumi/moegirl_mapper.py

bangumi/bgm_images_medium_mapped.json &: bangumi/subsets moegirl/subsets bangumi/moegirl2bgm.json bangumi/bgm_chars_full.json
	$(PYTHON) bangumi/crawler/img_preloader.py

.PHONY:bangumi/subsets
bangumi/subsets: bangumi/bgm_index_full.json bangumi/bgm2moegirl.json bangumi/moegirl2bgm.json moegirl/preprocess/char_index.json
	$(PYTHON) bangumi/subset/subsetter.py

bangumi/anime_character_guessr/id_tags.js bangumi/anime_character_guessr/id_tags.json &: bangumi/anime_character_guessr/tags.character_tags.json bangumi/bgm2moegirl.json bangumi/bgm_index_full.json moegirl/preprocess/char2attr.json moegirl/preprocess/attr2char.json moegirl/preprocess/fundamental_attr.json
	$(PYTHON) bangumi/anime_character_guessr/anime_character_guessr_mapper.py

.PHONY: anime_character_guessr
anime_character_guessr: bangumi/anime_character_guessr/id_tags.js