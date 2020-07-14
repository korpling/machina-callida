/* tslint:disable:no-string-literal */
import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController, ToastController} from '@ionic/angular';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import {ExerciseService} from 'src/app/exercise.service';
import {CorpusService} from 'src/app/corpus.service';
import {take} from 'rxjs/operators';
import { version } from 'src/version';
import configMC from '../../configMC';

@Component({
    selector: 'app-home',
    templateUrl: 'home.page.html',
    styleUrls: ['home.page.scss'],
})
export class HomePage implements OnInit {
    public configMC = configMC;
    public isCorpusUpdateInProgress = false;
    public version: string;

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public exerciseService: ExerciseService,
                public translate: TranslateService,
                public corpusService: CorpusService,
                public toastCtrl: ToastController,
                public helperService: HelperService,
    ) {
    }

    changeLanguage(newLanguage: string): Promise<void> {
        return new Promise<void>(resolve => {
            if (this.translate.currentLang !== newLanguage) {
                this.translate.use(newLanguage).pipe(take(1)).subscribe(() => {
                    this.helperService.loadTranslations(this.translate);
                    this.corpusService.initPhenomenonMap();
                    this.corpusService.processAnnisResponse(this.corpusService.annisResponse);
                    this.corpusService.adjustTranslations().then();
                    return resolve();
                });
            } else {
                return resolve();
            }
        });
    }

    ionViewDidEnter(): void {
        this.helperService.loadTranslations(this.translate);
    }

    ngOnInit(): void {
        // fix footer layout on IE11
        if (this.helperService.isIE11) {
            const tabs: HTMLIonTabsElement = document.querySelector('#tabs') as HTMLIonTabsElement;
            if (tabs) {
                tabs.style.maxWidth = '65%';
            }
        }
        this.version = version;
    }

    refreshCorpora(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.isCorpusUpdateInProgress = true;
            this.corpusService.getCorpora(0).then(() => {
                this.isCorpusUpdateInProgress = false;
                this.helperService.showToast(this.toastCtrl, this.helperService.corpusUpdateCompletedString).then();
                return resolve();
            }, async (error: HttpErrorResponse) => {
                this.isCorpusUpdateInProgress = false;
                return reject();
            });
        });
    }
}
