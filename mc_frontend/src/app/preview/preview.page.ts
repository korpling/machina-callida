/* tslint:disable:no-string-literal */
import {EventMC, ExerciseType} from 'src/app/models/enum';
import {HelperService} from 'src/app/helper.service';
import {NavController, ToastController} from '@ionic/angular';
import {ExerciseService} from 'src/app/exercise.service';
import {CorpusService} from 'src/app/corpus.service';
import {Component, OnDestroy, OnInit} from '@angular/core';
import {TranslateService} from '@ngx-translate/core';
import {HttpClient} from '@angular/common/http';
import {XAPIevent} from 'src/app/models/xAPIevent';
import {TestResultMC} from 'src/app/models/testResultMC';
import configMC from '../../configMC';
import {Storage} from '@ionic/storage';
import {AnnisResponse, Solution, FileType} from '../../../openapi';

@Component({
    selector: 'app-preview',
    templateUrl: './preview.page.html',
    styleUrls: ['./preview.page.scss'],
})
export class PreviewPage implements OnDestroy, OnInit {
    public configMC = configMC;
    public ExerciseType = ExerciseType;
    public FileType = FileType;
    public currentSolutions: Solution[];
    public inputSelector = 'input[type="text"]';
    public maxGapLength = 0;
    public showShareLink = false;
    public showInstructions = false;
    public solutionIndicesString: string;
    public solutionNodeIdSet: Set<string> = new Set<string>();
    public urlBase: string;

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public exerciseService: ExerciseService,
                public translateService: TranslateService,
                public corpusService: CorpusService,
                public helperService: HelperService,
                public toastCtrl: ToastController,
                public storage: Storage) {
    }

    async copyLink(): Promise<void> {
        const input: HTMLInputElement = document.querySelector(this.inputSelector);
        input.select();
        document.execCommand('copy');
        input.setSelectionRange(0, 0);
        this.helperService.showToast(this.toastCtrl, this.corpusService.shareLinkCopiedString, 'middle').then();
    }

    getSolutionIndices(solutions: Solution[]): string {
        const indices: string[] =
            solutions.map(x => this.corpusService.annisResponse.solutions.indexOf(x).toString());
        return '&solution_indices=' + indices.join(',');
    }

    initH5P(): void {
        const solutionIndicesString: string = this.exerciseService.excludeOOV ?
            this.getSolutionIndices(this.currentSolutions) : '';
        // this will be called via GET request from the h5p standalone javascript library
        const url: string = `${configMC.backendBaseUrl + configMC.backendApiH5pPath}` +
            `?eid=${this.corpusService.annisResponse.exercise_id}&lang=${this.translateService.currentLang + solutionIndicesString}`;
        this.exerciseService.setH5Purl(url);
        const exerciseTypePath: string = this.corpusService.exercise.type === ExerciseType.markWords ? 'mark_words' : 'drag_text';
        this.exerciseService.initH5P(exerciseTypePath).then();
        this.updateFileUrl();
    }

    ngOnDestroy(): void {
        this.helperService.getH5P().externalDispatcher.off(EventMC.xAPI);
    }

    ngOnInit(): Promise<void> {
        return new Promise<void>((resolve) => {
            this.currentSolutions = [];
            if (!this.helperService.isVocabularyCheck) {
                this.exerciseService.excludeOOV = false;
            }
            this.setXAPIeventHandler();
            this.corpusService.checkAnnisResponse().then(() => {
                this.processAnnisResponse(this.corpusService.annisResponse);
                this.initH5P();
                return resolve();
            }, () => {
                return resolve();
            });
        });
    }

    processAnnisResponse(ar: AnnisResponse): void {
        this.corpusService.annisResponse.solutions = ar.solutions;
        this.processSolutions(ar.solutions);
        this.corpusService.annisResponse.uri = ar.uri;
        const isUrn: boolean = this.corpusService.currentUrn && this.corpusService.currentUrn.startsWith('urn:');
        this.corpusService.annisResponse.graph_data.nodes = isUrn ? this.corpusService.annisResponse.graph_data.nodes : ar.graph_data.nodes;
        this.corpusService.annisResponse.graph_data.links = isUrn ? this.corpusService.annisResponse.graph_data.links : ar.graph_data.links;
    }

    processSolutions(solutions: Solution[]): void {
        const isCloze: boolean = this.corpusService.exercise.type === ExerciseType.cloze;
        if (this.exerciseService.excludeOOV) {
            const nodeIdSet: Set<string> = new Set(this.corpusService.annisResponse.graph_data.nodes.filter(
                x => !x.is_oov).map(x => x.id));
            solutions = this.corpusService.annisResponse.solutions.filter(
                x => nodeIdSet.has(x.target.salt_id) && (isCloze || nodeIdSet.has(x.value.salt_id)));
        }
        let newSolutions: Solution[];
        if (isCloze) {
            this.maxGapLength = Math.max.apply(Math, solutions.map(x => x.target.content.length));
            this.solutionNodeIdSet = new Set(solutions.map(x => x.target.salt_id));
            newSolutions = solutions.concat();
        } else {
            newSolutions = solutions.concat().sort((s1, s2) => {
                return s1.target.content < s2.target.content ? -1 : (s1.target.content > s2.target.content ? 1 : 0);
            });
        }
        this.currentSolutions = newSolutions;
    }

    selectLink(): void {
        const ta: HTMLTextAreaElement = document.querySelector(this.inputSelector);
        ta.select();
    }

    sendData(result: TestResultMC): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const fileUrl: string = configMC.backendBaseUrl + configMC.backendApiFilePath;
            const formData = new FormData();
            formData.append('learning_result', JSON.stringify({0: result.statement}));
            this.helperService.makePostRequest(this.http, this.toastCtrl, fileUrl, formData, '').then(() => {
                return resolve();
            }, () => {
                console.log('ERROR: COULD NOT SEND EXERCISE RESULTS TO SERVER.');
                return reject();
            });
        });
    }

    setXAPIeventHandler() {
        this.helperService.getH5P().externalDispatcher.on(EventMC.xAPI, (event: XAPIevent) => {
            // results are only available when a task has been completed/answered, not in the "attempted" or "interacted" stages
            if (event.data.statement.verb.id === configMC.xAPIverbIDanswered && event.data.statement.result) {
                const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
                if (iframe) {
                    const iframeDoc: Document = iframe.contentWindow.document;
                    const inner: string = iframeDoc.documentElement.innerHTML;
                    const result: TestResultMC = new TestResultMC({
                        statement: event.data.statement,
                        innerHTML: inner
                    });
                    this.sendData(result).then();
                }
            }
        });
    }

    switchOOV(): void {
        this.currentSolutions = [];
        this.processSolutions(this.corpusService.annisResponse.solutions);
        this.initH5P();
    }

    updateFileUrl(): void {
        const fileId: string = this.corpusService.annisResponse.exercise_id;
        const fileTypeBase = '&type=';
        this.urlBase = configMC.backendBaseUrl + configMC.backendApiFilePath + '?id=' + fileId + fileTypeBase;
        this.solutionIndicesString = '';
        if (this.exerciseService.excludeOOV) {
            this.solutionIndicesString = this.getSolutionIndices(this.currentSolutions);
        }
    }
}
