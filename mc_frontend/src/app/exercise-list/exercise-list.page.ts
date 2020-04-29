/* tslint:disable:no-string-literal */
import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController, ToastController} from '@ionic/angular';
import {ExerciseMC} from 'src/app/models/exerciseMC';
import {HttpClient, HttpParams} from '@angular/common/http';
import {
    ExerciseType,
    ExerciseTypeTranslation,
    MoodleExerciseType,
    SortingCategory,
    VocabularyCorpus,
    VocabularyCorpusTranslation
} from '../models/enum';
import {TranslateService} from '@ngx-translate/core';
import {AnnisResponse} from 'src/app/models/annisResponse';
import {CorpusService} from 'src/app/corpus.service';
import {VocabularyService} from 'src/app/vocabulary.service';
import {Storage} from '@ionic/storage';
import configMC from '../../configMC';
import {UpdateInfo} from '../models/updateInfo';
import {take} from 'rxjs/operators';
import {ApplicationState} from '../models/applicationState';

@Component({
    selector: 'app-exercise-list',
    templateUrl: './exercise-list.page.html',
    styleUrls: ['./exercise-list.page.scss'],
})
export class ExerciseListPage implements OnInit {

    public availableExercises: ExerciseMC[];
    public currentSearchValue: string;
    public currentSortingCategory: SortingCategory = SortingCategory.dateDesc;
    public exercises: ExerciseMC[] = [];
    public hasVocChanged = false;
    public Math = Math;
    public metadata: { [eid: string]: string } = {};
    public ObjectKeys = Object.keys;
    public showVocabularyCorpus = false;
    public SortingCategory = SortingCategory;
    public sortingCategoriesAsc: Set<SortingCategory> = new Set<SortingCategory>([
        SortingCategory.vocAsc, SortingCategory.authorAsc, SortingCategory.dateAsc, SortingCategory.typeAsc,
        SortingCategory.complexityAsc]);
    public sortingCategoriesMap: { [sc: string]: string } = {
        [SortingCategory.authorAsc]: 'work_author',
        [SortingCategory.authorDesc]: 'work_author',
        [SortingCategory.complexityAsc]: 'text_complexity',
        [SortingCategory.complexityDesc]: 'text_complexity',
        [SortingCategory.dateAsc]: 'last_access_time',
        [SortingCategory.dateDesc]: 'last_access_time',
        [SortingCategory.typeAsc]: 'exercise_type_translation',
        [SortingCategory.typeDesc]: 'exercise_type_translation',
        [SortingCategory.vocAsc]: 'matching_degree',
        [SortingCategory.vocDesc]: 'matching_degree',
    };
    public sortingCategoriesVocCheck: Set<SortingCategory> = new Set([SortingCategory.vocAsc, SortingCategory.vocDesc]);
    public VocabularyCorpus = VocabularyCorpus;
    public VocabularyCorpusTranslation = VocabularyCorpusTranslation;

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translateService: TranslateService,
                public helperService: HelperService,
                public corpusService: CorpusService,
                public storage: Storage,
                public toastCtrl: ToastController,
                public vocService: VocabularyService) {
    }

    filterExercises(searchValue: string): void {
        if (!searchValue) {
            this.exercises = this.availableExercises;
        } else {
            const searchValueLower: string = searchValue.toLowerCase();
            const metadata = this.metadata;
            this.exercises = this.availableExercises.filter((exercise: ExerciseMC) => {
                return metadata[exercise.eid].toLowerCase().includes(searchValueLower);
            });
        }
        this.sortExercises();
    }

    getDateString(dateMilliseconds: number): string {
        return new Date(dateMilliseconds).toLocaleDateString();
    }

    getExerciseList(force: boolean = false): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiExerciseListPath;
            this.hasVocChanged = false;
            let params: HttpParams = new HttpParams().set('lang', this.translateService.currentLang);
            this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                this.storage.get(configMC.localStorageKeyUpdateInfo).then((jsonString: string) => {
                    const updateInfo: UpdateInfo = JSON.parse(jsonString) as UpdateInfo;
                    // if there are no exercises in the cache, force refresh
                    const lastUpdateTime: number = force ? 0 : (state.exerciseList.length ? updateInfo.exerciseList : 0);
                    params = params.set('last_update_time', lastUpdateTime.toString());
                    if (this.vocService.currentReferenceVocabulary) {
                        params = params.set('vocabulary', VocabularyCorpus[this.vocService.currentReferenceVocabulary]);
                        params = params.set('frequency_upper_bound', this.vocService.frequencyUpperBound.toString());
                    }
                    this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((exercises: ExerciseMC[]) => {
                        updateInfo.exerciseList = new Date().getTime();
                        this.storage.set(configMC.localStorageKeyUpdateInfo, JSON.stringify(updateInfo)).then();
                        state.exerciseList = this.availableExercises = this.exercises = exercises;
                        this.helperService.saveApplicationState(state).then();
                        this.processExercises();
                        return resolve();
                    }, () => {
                        this.availableExercises = this.exercises = state.exerciseList;
                        this.processExercises();
                        return reject();
                    });
                });
            });
        });
    }

    getMatchingDegree(exercise: ExerciseMC): string {
        return exercise.matching_degree ? Math.round(exercise.matching_degree).toString() : '';
    }

    ngOnInit(): void {
        this.vocService.currentReferenceVocabulary = null;
        this.getExerciseList().then();
    }

    public processExercises(): void {
        this.exercises.forEach((exercise: ExerciseMC) => {
            this.translateService.get(ExerciseTypeTranslation[MoodleExerciseType[exercise.exercise_type]]).subscribe(
                value => exercise.exercise_type_translation = value);
            this.metadata[exercise.eid] = [exercise.work_author, exercise.exercise_type_translation, exercise.work_title]
                .join(' ').toLowerCase();
        });
        this.filterExercises(this.currentSearchValue);
    }

    showExercise(exercise: ExerciseMC): Promise<void> {
        return new Promise<void>((resolve) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiExercisePath;
            const params: HttpParams = new HttpParams().set('eid', exercise.eid);
            this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((ar: AnnisResponse) => {
                // save this exercise only locally in the CorpusService (not as MostRecentSetup in the HelperService) because
                // users just want to have a quick look at it
                this.corpusService.annisResponse = ar;
                const met: MoodleExerciseType = MoodleExerciseType[exercise.exercise_type];
                this.corpusService.exercise.type = ExerciseType[met.toString()];
                this.helperService.goToPreviewPage(this.navCtrl).then();
                return resolve();
            }, () => {
                return resolve();
            });
        });
    }

    sortExercises(): void {
        if (!this.exercises.length ||
            this.sortingCategoriesVocCheck.has(this.currentSortingCategory) && !this.exercises.some(x => !!x.matching_degree)) {
            return;
        }
        const property: string = this.sortingCategoriesMap[this.currentSortingCategory.toString()];
        if (this.sortingCategoriesAsc.has(this.currentSortingCategory)) {
            this.exercises.sort((a: ExerciseMC, b: ExerciseMC) => {
                return a[property] === b[property] ? 0 : (a[property] < b[property] ? -1 : 1);
            });
        } else {
            this.exercises.sort((a: ExerciseMC, b: ExerciseMC) => {
                return a[property] === b[property] ? 0 : (a[property] < b[property] ? 1 : -1);
            });
        }
    }

    toggleVocCorpus(): void {
        this.showVocabularyCorpus = !this.showVocabularyCorpus;
        if (this.showVocabularyCorpus && !this.vocService.currentReferenceVocabulary) {
            this.vocService.currentReferenceVocabulary = VocabularyCorpus.bws;
            this.hasVocChanged = true;
        }
        const iRowElement: HTMLIonRowElement = document.querySelector('#vocCorpus');
        iRowElement.style.display = this.showVocabularyCorpus ? 'block' : 'none';
    }
}
