/* tslint:disable:no-string-literal */
import {Component, OnInit} from '@angular/core';
import {HelperService} from '../helper.service';
import {NavController, ToastController} from '@ionic/angular';
import {ActivatedRoute} from '@angular/router';
import {TranslateService} from '@ngx-translate/core';
import {ExerciseService} from 'src/app/exercise.service';
import {HttpClient, HttpParams} from '@angular/common/http';
import {AnnisResponse} from 'src/app/models/annisResponse';
import {ExerciseType, MoodleExerciseType} from 'src/app/models/enum';
import {CorpusService} from 'src/app/corpus.service';
import {ApplicationState} from '../models/applicationState';
import {take} from 'rxjs/operators';
import configMC from '../../configMC';
import {Storage} from '@ionic/storage';

@Component({
    selector: 'app-exercise',
    templateUrl: './exercise.page.html',
    styleUrls: ['./exercise.page.scss'],
})
export class ExercisePage implements OnInit {

    constructor(public navCtrl: NavController,
                public activatedRoute: ActivatedRoute,
                public translateService: TranslateService,
                public exerciseService: ExerciseService,
                public http: HttpClient,
                public toastCtrl: ToastController,
                public helperService: HelperService,
                public corpusService: CorpusService,
                public storage: Storage) {
    }

    loadExercise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.activatedRoute.queryParams.subscribe((params: object) => {
                if (params['eid']) {
                    let url: string = configMC.backendBaseUrl + configMC.backendApiExercisePath;
                    const httpParams: HttpParams = new HttpParams().set('eid', params['eid']);
                    this.helperService.makeGetRequest(this.http, this.toastCtrl, url, httpParams).then((ar: AnnisResponse) => {
                        this.helperService.applicationState.pipe(take(1)).subscribe((as: ApplicationState) => {
                            as.mostRecentSetup.annisResponse = ar;
                            this.helperService.saveApplicationState(as).then();
                            this.corpusService.annisResponse = ar;
                            const met: MoodleExerciseType = MoodleExerciseType[ar.exercise_type];
                            this.corpusService.exercise.type = ExerciseType[met.toString()];
                            // this will be called via GET request from the h5p standalone javascript library
                            url = `${configMC.backendBaseUrl}${configMC.backendApiH5pPath}` +
                                `?eid=${this.corpusService.annisResponse.exercise_id}&lang=${this.translateService.currentLang}`;
                            this.storage.set(configMC.localStorageKeyH5P, url).then();
                            const exerciseTypePath: string = this.corpusService.exercise.type === ExerciseType.markWords ?
                                configMC.excerciseTypePathMarkWords : 'drag_text';
                            this.exerciseService.initH5P(exerciseTypePath).then(() => {
                                return resolve();
                            });
                        });
                    }, () => {
                        return reject();
                    });
                } else {
                    const exerciseType: string = params['type'];
                    const exerciseTypePath: string = exerciseType === this.exerciseService.vocListString ?
                        this.exerciseService.fillBlanksString : exerciseType;
                    const file: string = params['file'];
                    const lang: string = this.translateService.currentLang;
                    this.storage.set(configMC.localStorageKeyH5P,
                        this.helperService.baseUrl + '/assets/h5p/' + exerciseType + '/content/' + file + '_' + lang + '.json')
                        .then();
                    this.exerciseService.initH5P(exerciseTypePath).then(() => {
                        return resolve();
                    });
                }
            });
        });
    }

    ngOnInit(): Promise<void> {
        return new Promise<void>(resolve => {
            this.corpusService.checkAnnisResponse().then(() => {
                this.loadExercise().then(() => {
                    return resolve();
                });
            }, () => {
                return resolve();
            });
        });
    }

}
