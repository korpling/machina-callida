/* tslint:disable:no-string-literal */
import {Injectable} from '@angular/core';
import configMC from '../configMC';
import {HelperService} from './helper.service';
import {ExercisePart} from './models/exercisePart';
import {DisplayOptions, Options} from './models/h5p-standalone.class';
import {EventMC, ExerciseType, MoodleExerciseType} from './models/enum';
import {HttpClient, HttpParams} from '@angular/common/http';
import {AnnisResponse} from '../../openapi';
import {take} from 'rxjs/operators';
import {ApplicationState} from './models/applicationState';
import {ToastController} from '@ionic/angular';
import {CorpusService} from './corpus.service';
import {TranslateService} from '@ngx-translate/core';
import {Storage} from '@ionic/storage';
import {ExerciseParams} from './models/exerciseParams';

declare var H5PStandalone: any;

@Injectable({
    providedIn: 'root'
})
export class ExerciseService {
    // tslint:disable-next-line:variable-name
    private _currentExerciseIndex: number;
    get currentExerciseIndex(): number {
        return this._currentExerciseIndex;
    }

    set currentExerciseIndex(value: number) {
        this._currentExerciseIndex = value;
        this.currentExercisePartIndex = [...Array(this.currentExerciseParts.length).keys()].find(
            i => this.currentExerciseParts[i].startIndex <= this.currentExerciseIndex &&
                (!this.currentExerciseParts[i + 1] || this.currentExerciseParts[i + 1].startIndex > this.currentExerciseIndex));
        const cepi: number = this.currentExercisePartIndex;
        this.currentExerciseName = this.currentExercisePartIndex ?
            this.currentExerciseParts[cepi].exercises[this.currentExerciseIndex - this.currentExerciseParts[cepi].startIndex] :
            '';
    }

    public currentExerciseName: string;
    public currentExercisePartIndex: number;
    public currentExerciseParts: ExercisePart[] = [];
    public displayOptions: DisplayOptions = { // Customise the look of the H5P
        frame: true,
        copyright: true,
        embed: true,
        download: true,
        icon: true,
        export: true
    };
    public embedButtonString = '.h5p-embed';
    public embedSizeInputString = '.h5p-embed-size';
    public embedTextAreaString = '.h5p-embed-code-container';
    public excludeOOV = false;
    public fillBlanksString = 'fill_blanks';
    public h5pContainerString = '.h5p-container';
    public h5pIframeString = '.h5p-iframe';
    public kwicGraphs: string;
    public options: Options = {
        frameCss: 'assets/h5p-standalone-master/dist/styles/h5p.css',
        frameJs: 'assets/h5p-standalone-master/dist/frame.bundle.js',
        preventH5PInit: false
    };
    public vocListString = 'voc_list';

    constructor(public helperService: HelperService,
                public http: HttpClient,
                public toastCtrl: ToastController,
                public corpusService: CorpusService,
                public storage: Storage,
                public translateService: TranslateService) {
    }

    createGuid(): string {
        function s4(): string {
            return Math.floor((1 + Math.random()) * 0x10000)
                .toString(16)
                .substring(1);
        }

        return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
    }

    createH5Pstandalone(el: HTMLElement, h5pLocation: string, options: Options, displayOptions: DisplayOptions): Promise<void> {
        return new H5PStandalone.H5P(el, h5pLocation, options, displayOptions);
    }

    getH5Pelements(selector: string, multi: boolean = false): any {
        const iframe: HTMLIFrameElement = document.querySelector(this.h5pIframeString);
        if (!iframe) {
            return iframe;
        }
        return multi ? iframe.contentWindow.document.querySelectorAll(selector) : iframe.contentWindow.document.querySelector(selector);
    }

    initH5P(exerciseTypePath: string, showActions: boolean = true): Promise<void> {
        return new Promise((resolve) => {
            const el: HTMLDivElement = document.querySelector(this.h5pContainerString);
            const h5pLocation = 'assets/h5p/' + exerciseTypePath;
            const displayOptions: DisplayOptions = this.helperService.deepCopy(this.displayOptions);
            if (!showActions) {
                displayOptions.embed = false;
                displayOptions.export = false;
            }
            this.createH5Pstandalone(el, h5pLocation, this.options, displayOptions).then(() => {
                // dirty hack to wait for all the H5P elements being added to the DOM
                setTimeout(() => {
                    this.helperService.events.trigger(EventMC.h5pCreated, {data: {library: exerciseTypePath}});
                    this.setH5PeventHandlers();
                    return resolve();
                }, 300);
            });
        });
    }

    loadExercise(params: ExerciseParams): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            if (params.eid) {
                const url: string = configMC.backendBaseUrl + configMC.backendApiExercisePath;
                const httpParams: HttpParams = new HttpParams().set('eid', params.eid);
                this.helperService.makeGetRequest(this.http, this.toastCtrl, url, httpParams).then((ar: AnnisResponse) => {
                    this.helperService.applicationState.pipe(take(1)).subscribe((as: ApplicationState) => {
                        as.mostRecentSetup.annisResponse = this.corpusService.annisResponse = ar;
                        this.helperService.saveApplicationState(as).then();
                        const met: MoodleExerciseType = MoodleExerciseType[ar.exercise_type];
                        this.corpusService.exercise.type = ExerciseType[met.toString()];
                        this.loadH5P(this.corpusService.annisResponse.exercise_id).then(() => {
                            return resolve();
                        });
                    });
                }, () => {
                    return reject();
                });
            } else {
                const exerciseType: string = params.type;
                const exerciseTypePath: string = exerciseType === this.vocListString ? this.fillBlanksString : exerciseType;
                const file: string = params.file;
                const lang: string = this.translateService.currentLang;
                this.storage.set(configMC.localStorageKeyH5P,
                    this.helperService.baseUrl + '/assets/h5p/' + exerciseType + '/content/' + file + '_' + lang + '.json')
                    .then();
                this.initH5P(exerciseTypePath).then(() => {
                    return resolve();
                });
            }
        });
    }

    loadH5P(eid: string): Promise<void> {
        // this will be called via GET request from the h5p standalone javascript library
        const url: string = `${configMC.backendBaseUrl}${configMC.backendApiH5pPath}` +
            `?eid=${eid}&lang=${this.translateService.currentLang}`;
        this.storage.set(configMC.localStorageKeyH5P, url).then();
        const exerciseTypePath: string = this.corpusService.exercise.type === ExerciseType.markWords ?
            configMC.excerciseTypePathMarkWords : configMC.exerciseTypePathDragText;
        return this.initH5P(exerciseTypePath);
    }

    setH5PeventHandlers(): void {
        const embedButton: HTMLUListElement = this.getH5Pelements(this.embedButtonString);
        if (embedButton) {
            embedButton.addEventListener('click', () => {
                setTimeout(() => {
                    const inputs: NodeListOf<HTMLInputElement> = this.getH5Pelements(this.embedSizeInputString, true);
                    inputs.forEach(input => input.addEventListener('change', this.updateEmbedUrl.bind(this)));
                    this.updateEmbedUrl();
                }, 300);
            });
        }
    }

    setH5Purl(url: string): void {
        // this has to be LocalStorage because the H5P javascript cannot easily access the Ionic Storage
        window.localStorage.setItem(configMC.localStorageKeyH5P, url);
    }

    updateEmbedUrl(): void {
        const embedTextarea: HTMLTextAreaElement = this.getH5Pelements(this.embedTextAreaString);
        const baseUrl: string = configMC.frontendBaseUrl + configMC.pageUrlEmbed;
        const eid: string = this.corpusService.annisResponse.exercise_id;
        const inputs: NodeListOf<HTMLInputElement> = this.getH5Pelements(this.embedSizeInputString, true);
        const width: string = inputs[0].value;
        const height: string = inputs[1].value;
        embedTextarea.innerHTML =
            `<iframe src="${baseUrl}?eid=${eid}" width="${width}px" height="${height}px" allowfullscreen="allowfullscreen"></iframe>
<script src="https://h5p.org/sites/all/modules/h5p/library/js/h5p-resizer.js" charset="UTF-8"></script>`;
    }
}
