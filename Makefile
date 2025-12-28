PYTHON := $(if $(PYTHON),$(PYTHON),python3)

PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
export PYTHONPATH = $(PROJECT_ROOT)

.PHONY: clean_all
clean_all:
# 	@read -p "Are you sure? [y/N] " ans && ans=$${ans:-N} ; \
# 	if [ $${ans} = y ] || [ $${ans} = Y ]; then \
# 		printf "YES\n" ; \
# 	else \
# 		printf "NO\n" ; exit 1; \
# 	fi

	rm -rf moegirl/attrs.partial.json
	rm -rf moegirl/subjects.partial.json
	rm -rf moegirl/extra_info.partial.json

	rm -rf moegirl/attrs.json
	rm -rf moegirl/subjects.json
	rm -rf moegirl/extra_info.json
# 	rm -rf bangumi/bgm_images_medium_mapped.json

	rm -rf moegirl/attr_index.json
	rm -rf moegirl/attr2char.json
	rm -rf moegirl/attr2article.json
	rm -rf moegirl/char_index.json
	rm -rf moegirl/char2attr.json
	rm -rf moegirl/char2cv.json
	rm -rf moegirl/cv_index.json
	rm -rf moegirl/cv2char.json 
	rm -rf moegirl/char2subject.json
	rm -rf moegirl/subject_index.json
	rm -rf moegirl/fundamental_attr.json
	rm -rf moegirl/extra_processed.json
	rm -rf moegirl/char2gender.json
	rm -rf moegirl/subset/*
	rm -rf moegirl/analysis/*.npy
	rm -rf moegirl/moeranker/data_min.json
	rm -rf moegirl/moeranker/importance.json

	rm -rf bangumi/dump/*.zip
	rm -rf bangumi/dump/*.jsonlines
	rm -rf bangumi/bgm_chars_full.json
	rm -rf bangumi/bgm_index_full.json
# 	rm -rf bangumi/bgm_redirects_full.json
	rm -rf bangumi/bgm_subjects_full.json
	rm -rf bangumi/moegirl2bgm.json
	rm -rf bangumi/bgm2moegirl.json
	rm -rf bangumi/bgm_info.json
	rm -rf bangumi/subset/*
	rm -rf bangumi/anime_character_guessr/id_tags.js
	rm -rf bangumi/anime_character_guessr/id_tags.json

.PHONY: clean
clean: 
# 	@read -p "Are you sure? [y/N] " ans && ans=$${ans:-N} ; \
# 	if [ $${ans} = y ] || [ $${ans} = Y ]; then \
# 		printf "YES\n" ; \
# 	else \
# 		printf "NO\n" ; exit 1; \
# 	fi

	rm -rf moegirl/attr_index.json
	rm -rf moegirl/attr2char.json
	rm -rf moegirl/attr2article.json
	rm -rf moegirl/char_index.json
	rm -rf moegirl/char2attr.json
	rm -rf moegirl/char2cv.json
	rm -rf moegirl/cv_index.json
	rm -rf moegirl/cv2char.json 
	rm -rf moegirl/char2subject.json
	rm -rf moegirl/subject_index.json
	rm -rf moegirl/fundamental_attr.json
# 	rm -rf moegirl/extra_processed.json
	rm -rf moegirl/char2gender.json
	rm -rf moegirl/subset/*
	rm -rf moegirl/analysis/*.npy
	rm -rf moegirl/moeranker/data_min.json
	rm -rf moegirl/moeranker/importance.json

	rm -rf bangumi/dump_converter/*.zip
	rm -rf bangumi/dump_converter/*.jsonlines
	rm -rf bangumi/bgm_chars_full.json
	rm -rf bangumi/bgm_index_full.json
# 	rm -rf bangumi/bgm_redirects_full.json
	rm -rf bangumi/bgm_subjects_full.json
	rm -rf bangumi/moegirl2bgm.json
	rm -rf bangumi/bgm2moegirl.json
	rm -rf bangumi/bgm_info.json
	rm -rf bangumi/subset/*
	rm -rf bangumi/anime_character_guessr/id_tags.js
	rm -rf bangumi/anime_character_guessr/id_tags.json

.PHONY: all
all: moegirl/attrs.json moegirl/subjects.json moegirl/attr_index.json moegirl/attr2char.json moegirl/attr2article.json moegirl/char_index.json moegirl/char2attr.json moegirl/char2cv.json moegirl/cv_index.json moegirl/cv2char.json  moegirl/char2subject.json moegirl/subject_index.json moegirl/fundamental_attr.json moegirl/extra_processed.json moegirl/subsets moegirl/analysis/intersection.npy moegirl/analysis/cross.npy moegirl/analysis/count.npy moegirl/analysis/contain.npy moegirl/analysis/gain.npy moegirl/analysis/chi2.npy moegirl/char2gender.json moeranker/data_min.json moeranker/importance.json bangumi/bgm_chars_full.json bangumi/bgm_index_full.json bangumi/bgm_redirects_full.json bangumi/bgm_subjects_full.json bangumi/moegirl2bgm.json bangumi/bgm2moegirl.json bangumi/bgm_info.json bangumi/subsets anime_character_guessr/id_tags.js anime_character_guessr/id_tags.json

moegirl/attrs.json moegirl/subjects.json &: src/moegirl/crawler/crawler.py
	$(PYTHON) src/moegirl/crawler/crawler.py

moegirl/attr_index.json moegirl/attr2char.json moegirl/attr2article.json moegirl/char_index.json moegirl/char2attr.json moegirl/char2cv.json moegirl/cv_index.json moegirl/cv2char.json &: src/moegirl/preprocess/flattener_attrs.py moegirl/attrs.json
	$(PYTHON) src/moegirl/preprocess/flattener_attrs.py

moegirl/char2subject.json moegirl/subject_index.json &: src/moegirl/preprocess/flattener_subjects.py moegirl/subjects.json moegirl/char_index.json
	$(PYTHON) src/moegirl/preprocess/flattener_subjects.py

moegirl/fundamental_attr.json: src/moegirl/preprocess/attr_filter.py moegirl/attr_index.json moegirl/attrs.json moegirl/attr2char.json moegirl/hair_color_attr.json moegirl/eye_color_attr.json
	$(PYTHON) src/moegirl/preprocess/attr_filter.py


moegirl/extra_info.json: src/moegirl/crawler/crawler_extra.py moegirl/char_index.json
	$(PYTHON) src/moegirl/crawler/crawler_extra.py

moegirl/extra_processed.json: src/moegirl/crawler/process_extra.py moegirl/extra_info.json
	$(PYTHON) src/moegirl/crawler/process_extra.py


.PHONY: moegirl/subsets
moegirl/subsets: src/moegirl/subset/subsetter.py moegirl/attrs.json moegirl/char2subject.json moegirl/char_index.json
	$(PYTHON) src/moegirl/subset/subsetter.py


moegirl/analysis/intersection.npy moegirl/analysis/cross.npy moegirl/analysis/count.npy &: src/moegirl/analysis/intersection.py moegirl/attr2char.json moegirl/char_index.json moegirl/attr_index.json
	$(PYTHON) src/moegirl/analysis/intersection.py

moegirl/analysis/contain.npy moegirl/analysis/gain.npy moegirl/analysis/chi2.npy &: src/moegirl/analysis/correlation.py moegirl/analysis/intersection.npy moegirl/char_index.json moegirl/attr_index.json
	$(PYTHON) src/moegirl/analysis/correlation.py

moegirl/char2gender.json &: src/moegirl/analysis/guess_gender.py moegirl/male_attr.json moegirl/female_attr.json moegirl/nogender_attr.json moegirl/char2attr.json bangumi/moegirl2bgm.json bangumi/bgm_chars_full.json
	$(PYTHON) src/moegirl/analysis/guess_gender.py


moeranker/data_min.json &: src/moeranker/minifier.py moegirl/char_index.json moegirl/attr_index.json moegirl/attr2char.json moegirl/char2attr.json moegirl/attr2article.json moegirl/char2gender.json
	$(PYTHON) src/moeranker/minifier.py

moeranker/importance.json &: src/moeranker/importance.py moegirl/attr_index.json moegirl/char_index.json moegirl/analysis/gain.npy moegirl/analysis/count.npy moegirl/analysis/contain.npy moegirl/analysis/intersection.npy moegirl/hair_color_attr.json moegirl/eye_color_attr.json
	$(PYTHON) src/moeranker/importance.py

.PHONY: moeranker
moeranker: moeranker/data_min.json moeranker/importance.json bangumi/moegirl2bgm.json bangumi/bgm_info.json moegirl/subsets bangumi/subsets


bangumi/bgm_chars_full.json bangumi/bgm_index_full.json bangumi/bgm_subjects_full.json &: src/bangumi/dump/dump_downloader.py src/bangumi/dump/dump_converter.py
	$(PYTHON) src/bangumi/dump/dump_downloader.py
	$(PYTHON) src/bangumi/dump/dump_converter.py
	rm -rf bangumi/dump/*.jsonlines

bangumi/bgm_redirects_full.json &: src/bangumi/dump/redirect_checker.py bangumi/bgm_chars_full.json bangumi/bgm_index_full.json bangumi/bgm_subjects_full.json
	$(PYTHON) src/bangumi/dump/redirect_checker.py

bangumi/moegirl2bgm.json bangumi/bgm2moegirl.json bangumi/bgm_info.json &: src/bangumi/moegirl_mapper.py bangumi/bgm_index_full.json bangumi/bgm_chars_full.json bangumi/bgm_subjects_full.json bangumi/bgm_redirects_full.json moegirl/char_index.json moegirl/extra_processed.json moegirl/char2subject.json
	$(PYTHON) src/bangumi/moegirl_mapper.py

bangumi/bgm_images_medium_mapped.json &: src/bangumi/crawler/img_preloader.py bangumi/subsets moegirl/subsets bangumi/moegirl2bgm.json bangumi/bgm_chars_full.json
	$(PYTHON) src/bangumi/crawler/img_preloader.py

.PHONY: bangumi/subsets
bangumi/subsets: src/bangumi/subsetter.py bangumi/bgm_index_full.json bangumi/bgm2moegirl.json bangumi/moegirl2bgm.json moegirl/char_index.json
	$(PYTHON) src/bangumi/subsetter.py

anime_character_guessr/id_tags.js anime_character_guessr/id_tags.json &: src/anime_character_guessr/anime_character_guessr_mapper.py anime_character_guessr/tags.character_tags.json bangumi/bgm2moegirl.json bangumi/bgm_index_full.json moegirl/char2attr.json moegirl/attr2char.json moegirl/fundamental_attr.json
	$(PYTHON) src/anime_character_guessr/anime_character_guessr_mapper.py

.PHONY: anime_character_guessr
anime_character_guessr: anime_character_guessr/id_tags.js