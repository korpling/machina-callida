/* tslint:disable:no-string-literal */
import {
    ExerciseType,
    ExerciseTypeTranslation,
    MoodleExerciseType,
    PhenomenonTranslation
} from '../models/enum';
import {NavController, ToastController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {Component, OnInit} from '@angular/core';
import {TranslateService} from '@ngx-translate/core';
import {ExerciseService} from 'src/app/exercise.service';
import {HelperService} from 'src/app/helper.service';
import {CorpusService} from 'src/app/corpus.service';
import {QueryMC} from 'src/app/models/queryMC';
import {PhenomenonMapContent} from 'src/app/models/phenomenonMap';
import {CorpusMC} from '../models/corpusMC';
import {ApplicationState} from '../models/applicationState';
import {take} from 'rxjs/operators';
import {TextRange} from '../models/textRange';
import configMC from '../../configMC';
import {AnnisResponse, ExerciseForm, FrequencyItem, Phenomenon} from '../../../openapi';
import {KwicForm} from '../../../openapi';

@Component({
    selector: 'app-exercise-parameters',
    templateUrl: './exercise-parameters.page.html',
    styleUrls: ['./exercise-parameters.page.scss'],
})
export class ExerciseParametersPage implements OnInit {
    public ExerciseType = ExerciseType;
    ExerciseTypeTranslation = ExerciseTypeTranslation;
    public leftContextSize = 5;
    public Math = Math;
    ObjectKeys = Object.keys;
    ObjectValues = Object.values;
    Phenomenon = Phenomenon;
    PhenomenonTranslation = PhenomenonTranslation;
    public rightContextSize = 5;
    showFeedback = false;

    constructor(public navCtrl: NavController,
                public toastCtrl: ToastController,
                public translateService: TranslateService,
                public corpusService: CorpusService,
                public exerciseService: ExerciseService,
                public http: HttpClient,
                public helperService: HelperService) {
    }

    generateExercise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const phenomenon: Phenomenon = this.corpusService.exercise.queryItems[0].phenomenon;
            if (0 < configMC.maxTextLength && configMC.maxTextLength < this.corpusService.currentText.length) {
                this.helperService.showToast(this.toastCtrl, this.corpusService.textTooLongString).then();
                return reject();
            } else if ((phenomenon === Phenomenon.Lemma && !this.corpusService.exercise.queryItems[0].values) ||
                this.corpusService.exercise.type === ExerciseType.matching && !this.corpusService.exercise.queryItems[1].values[0]) {
                this.helperService.showToast(this.toastCtrl, this.corpusService.emptyQueryValueString).then();
                return reject();
            } else {
                this.corpusService.annisResponse.solutions = null;
                this.getExerciseData().then(() => {
                    return resolve();
                });
            }
        });
    }

    public getDisplayValue(query: QueryMC, key: string, queryIndex: number = 0): string {
        const pmc: PhenomenonMapContent = this.corpusService.phenomenonMap[query.phenomenon];
        const translatedKey: string = pmc.translationValues[key];
        let count: number;
        if (this.corpusService.exercise.type === ExerciseType.matching) {
            if (queryIndex) {
                const relevantFI: FrequencyItem = this.corpusService.annisResponse.frequency_analysis.find(
                    x => x.values[0] === this.corpusService.exercise.queryItems[0].values[0] && x.values[1] === key);
                count = relevantFI.count;
            } else {
                const relevantFIs: FrequencyItem[] = this.corpusService.annisResponse.frequency_analysis.filter(
                    x => x.phenomena[0] === query.phenomenon && x.values[0] === key);
                count = relevantFIs.map(x => x.count).reduce((a, b) => a + b);
            }
        } else {
            count = pmc.specificValues[key];
        }
        return translatedKey + ' (' + count + ')';
    }

    getExerciseData(): Promise<void> {
        return new Promise<void>(resolve => {
            const searchValues: string[] = this.corpusService.exercise.queryItems.map(
                query => query.phenomenon + '=' + query.values.join('|'));
            let instructions: string = this.corpusService.exercise.instructionsTranslation;
            if (this.corpusService.exercise.type === ExerciseType.kwic) {
                this.getKwicExercise(JSON.stringify(searchValues)).then();
                return resolve();
            } else if (this.corpusService.exercise.type === ExerciseType.markWords) {
                const phenomenon: Phenomenon = this.corpusService.exercise.queryItems[0].phenomenon;
                const pmc: PhenomenonMapContent = this.corpusService.phenomenonMap[phenomenon];
                const values: string[] = this.corpusService.exercise.queryItems[0].values as string[];
                instructions += ` [${values.map(x => pmc.translationValues[x]).join(', ')}]`;
            }
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                    // TODO: change the corpus title to something meaningful, e.g. concatenate user ID and wanted exercise title
                    const workTitle: string = cc.title + ', ' + tr.start.filter(x => x).join('.') + '-' + tr.end.filter(x => x).join('.');
                    const ef: ExerciseForm = {
                        correct_feedback: this.corpusService.exercise.feedback.correct,
                        instructions,
                        general_feedback: this.corpusService.exercise.feedback.general,
                        incorrect_feedback: this.corpusService.exercise.feedback.incorrect,
                        language: this.translateService.currentLang,
                        partially_correct_feedback: this.corpusService.exercise.feedback.partiallyCorrect,
                        search_values: JSON.stringify(searchValues),
                        type: MoodleExerciseType[this.corpusService.exercise.type],
                        type_translation: this.corpusService.exercise.typeTranslation,
                        urn: this.corpusService.currentUrn,
                        work_author: cc.author,
                        work_title: workTitle,
                    };
                    this.getH5Pexercise(ef).then(() => {
                        return resolve();
                    });
                });
            });
        });
    }

    getH5Pexercise(ef: ExerciseForm): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiExercisePath;
            const formData = new FormData();
            Object.keys(ef).forEach((key: string) => {
                formData.append(key, ef[key]);
            });
            this.helperService.makePostRequest(this.http, this.toastCtrl, url, formData).then((ar: AnnisResponse) => {
                // save the old frequency analysis in case we want to change the exercise parameters at a later time
                ar.frequency_analysis = this.corpusService.annisResponse.frequency_analysis;
                this.helperService.applicationState.pipe(take(1)).subscribe((as: ApplicationState) => {
                    as.mostRecentSetup.annisResponse = ar;
                    this.helperService.saveApplicationState(as).then();
                    this.corpusService.annisResponse.exercise_id = ar.exercise_id;
                    this.corpusService.annisResponse.uri = ar.uri;
                    this.corpusService.annisResponse.solutions = ar.solutions;
                    this.helperService.goToPage(this.navCtrl, configMC.pageUrlPreview).then();
                    return resolve();
                });
            }, () => {
                return reject();
            });
        });
    }

    getKwicExercise(searchValues: string): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const kf: KwicForm = {
                ctx_left: (Math.max(Math.round(this.leftContextSize), 1)),
                ctx_right: Math.max(Math.round(this.rightContextSize), 1),
                search_values: searchValues,
                urn: this.corpusService.currentUrn
            };
            const formData = new FormData();
            Object.keys(kf).forEach((key: string) => {
                formData.append(key, kf[key]);
            });
            const kwicUrl: string = configMC.backendBaseUrl + configMC.backendApiKwicPath;
            this.helperService.makePostRequest(this.http, this.toastCtrl, kwicUrl, formData).then((svgString: string) => {
                this.exerciseService.kwicGraphs = svgString;
                this.helperService.goToPage(this.navCtrl, configMC.pageUrlKwic).then();
                return resolve();
            }, () => {
                return reject();
            });
        });
    }

    ngOnInit(): void {
        this.corpusService.adjustTranslations().then();
    }

}
