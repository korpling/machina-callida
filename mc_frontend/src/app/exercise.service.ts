/* tslint:disable:no-string-literal */
import {Injectable} from '@angular/core';
import configMC from '../configMC';
import {HelperService} from './helper.service';
import {ExercisePart} from './models/exercisePart';
import {EventMC, ExerciseType, MoodleExerciseType} from './models/enum';
import {HttpClient, HttpParams} from '@angular/common/http';
import {AnnisResponse, ExerciseTypePath, H5PForm} from '../../openapi';
import {take} from 'rxjs/operators';
import {ApplicationState} from './models/applicationState';
import {ToastController} from '@ionic/angular';
import {CorpusService} from './corpus.service';
import {TranslateService} from '@ngx-translate/core';
import {Storage} from '@ionic/storage';
import {ExerciseParams} from './models/exerciseParams';
import {DisplayOptions, Options} from './models/h5pStandalone';

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
    public downloadButtonString = '.h5p-scroll-content';
    public embedButtonString = '.h5p-embed';
    public embedSizeInputString = '.h5p-embed-size';
    public embedTextAreaString = '.h5p-embed-code-container';
    public excludeOOV = false;
    public h5pContainerString = '.h5p-container';
    public h5pIframeString = '.h5p-iframe';
    public kwicGraphs: string;
    public options: Options = {
        frameCss: 'assets/h5p-standalone-master/dist/styles/h5p.css',
        frameJs: 'assets/h5p-standalone-master/dist/frame.bundle.js',
        preventH5PInit: false
    };
    public reuseButtonString = '.h5p-export';

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

    downloadBlobAsFile(blob: Blob, fileName: string) {
        // Convert your blob into a special url that points to an object in the browser's memory
        const blobUrl: string = URL.createObjectURL(blob);
        // Create a link element
        const anchor: HTMLAnchorElement = document.createElement('a');
        // Set link's href to point to the Blob URL
        anchor.href = blobUrl;
        anchor.download = fileName;
        // Append link to the body
        document.body.appendChild(anchor);
        // Dispatch click event on the link
        // This is necessary as link.click() does not work on the latest firefox
        anchor.dispatchEvent(new MouseEvent('click',
            {bubbles: true, cancelable: true, view: window}));
        // Remove link from body
        document.body.removeChild(anchor);
    }

    downloadH5Pexercise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const url = `${configMC.backendBaseUrl}${configMC.backendApiH5pPath}`;
            const indices: number[] = this.corpusService.currentSolutions.map(
                x => this.corpusService.annisResponse.solutions.indexOf(x));
            const exerciseTypePath: ExerciseTypePath =
                this.corpusService.exercise.type === ExerciseType.markWords ?
                    ExerciseTypePath.MarkWords : ExerciseTypePath.DragText;
            const h5pForm: H5PForm = {
                eid: this.corpusService.annisResponse.exercise_id,
                exercise_type_path: exerciseTypePath,
                lang: this.translateService.currentLang,
                solution_indices: indices
            };
            const formData: FormData = new FormData();
            Object.keys(h5pForm).forEach((key: string) => formData.append(key, h5pForm[key]));
            const options = {responseType: 'blob' as const};
            const errorMsg: string = HelperService.generalErrorAlertMessage;
            this.helperService.makePostRequest(this.http, this.toastCtrl, url, formData, errorMsg, options)
                .then((result: Blob) => {
                    const fileName = exerciseTypePath + '.h5p';
                    this.downloadBlobAsFile(result, fileName);
                    return resolve();
                }, () => {
                    return reject();
                });
        });
    }

    getH5Pelements(selector: string, multi: boolean = false): any {
        const iframe: HTMLIFrameElement = this.getH5PIframe();
        if (!iframe) {
            return iframe;
        }
        return multi ? iframe.contentWindow.document.querySelectorAll(selector) :
            iframe.contentWindow.document.querySelector(selector);
    }

    getH5PIframe(): HTMLIFrameElement {
        return document.querySelector(this.h5pIframeString);
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
                const exerciseTypePath: string = exerciseType === ExerciseTypePath.VocList ?
                    ExerciseTypePath.FillBlanks : exerciseType;
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
            ExerciseTypePath.MarkWords : ExerciseTypePath.DragText;
        return this.initH5P(exerciseTypePath);
    }

    setH5PdownloadEventHandler(): void {
        const downloadButton: HTMLDivElement = this.getH5Pelements(this.downloadButtonString);
        const clonedButton: Node = downloadButton.cloneNode(true);
        downloadButton.parentNode.replaceChild(clonedButton, downloadButton);
        clonedButton.addEventListener('click', (downloadEvent: Event) => {
            downloadEvent.preventDefault();
            this.downloadH5Pexercise().then(() => {
            }, () => {
            });
        });
    }

    setH5PeventHandlers(): void {
        const loadingTime = 300;
        const embedButton: HTMLUListElement = this.getH5Pelements(this.embedButtonString);
        if (embedButton) {
            embedButton.addEventListener('click', () => {
                setTimeout(() => {
                    const inputs: NodeListOf<HTMLInputElement> = this.getH5Pelements(this.embedSizeInputString, true);
                    inputs.forEach(input => input.addEventListener('change', this.updateEmbedUrl.bind(this)));
                    this.updateEmbedUrl();
                }, loadingTime);
            });
        }
        const reuseButton: HTMLUListElement = this.getH5Pelements(this.reuseButtonString);
        if (reuseButton) {
            reuseButton.addEventListener('click', (reuseEvent: MouseEvent) => {
                reuseEvent.preventDefault();
                setTimeout(this.setH5PdownloadEventHandler.bind(this), loadingTime);
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
