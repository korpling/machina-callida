/* tslint:disable:no-string-literal */
import {Component, OnInit} from '@angular/core';
import {NavController, ToastController} from '@ionic/angular';
import {CorpusService} from 'src/app/corpus.service';
import {VocabularyService} from 'src/app/vocabulary.service';
import {ExerciseService} from 'src/app/exercise.service';
import {HelperService} from 'src/app/helper.service';
import {TranslateService} from '@ngx-translate/core';
import {VocabularyCorpus} from '../models/enum';
import {HttpClient} from '@angular/common/http';
import {CorpusMC} from '../models/corpusMC';
import {take} from 'rxjs/operators';
import configMC from '../../configMC';
import { FileType } from 'openapi';

@Component({
    selector: 'app-show-text',
    templateUrl: './show-text.page.html',
    styleUrls: ['./show-text.page.scss'],
})
export class ShowTextPage implements OnInit {
    FileType = FileType;
    ObjectKeys = Object.keys;
    public downloadLinkSelector = '#download';
    public highlightOOV = false;
    public isDownloading = false;
    public showTextComplexity = false;
    public showTextComplexityDoc = false;
    public text: string;
    public textComplexityMap = {
        all: 'TEXT_COMPLEXITY_ALL',
        n_w: 'TEXT_COMPLEXITY_WORD_COUNT',
        n_sent: 'TEXT_COMPLEXITY_SENTENCE_COUNT',
        avg_w_per_sent: 'TEXT_COMPLEXITY_AVERAGE_SENTENCE_LENGTH',
        avg_w_len: 'TEXT_COMPLEXITY_AVERAGE_WORD_LENGTH',
        n_types: 'TEXT_COMPLEXITY_TYPE_COUNT',
        pos: 'TEXT_COMPLEXITY_PART_OF_SPEECH_COUNT',
        lex_den: 'TEXT_COMPLEXITY_LEXICAL_DENSITY',
        n_punct: 'TEXT_COMPLEXITY_PUNCTUATION_COUNT',
        n_clause: 'TEXT_COMPLEXITY_CLAUSE_COUNT',
        n_subclause: 'TEXT_COMPLEXITY_SUBCLAUSE_COUNT',
        n_inf: 'TEXT_COMPLEXITY_INFINITIVE_COUNT',
        n_part: 'TEXT_COMPLEXITY_PARTICIPLE_COUNT',
        n_gerund: 'TEXT_COMPLEXITY_GERUND_COUNT',
        n_abl_abs: 'TEXT_COMPLEXITY_ABLATIVI_ABSOLUTI_COUNT'
    };
    public urlBase: string;

    constructor(public navCtrl: NavController,
                public corpusService: CorpusService,
                public exerciseService: ExerciseService,
                public toastCtrl: ToastController,
                public translateService: TranslateService,
                public vocService: VocabularyService,
                public http: HttpClient,
                public helperService: HelperService) {
    }

    generateDownloadLink(fileType: string): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const formData = new FormData();
            let content: string = document.querySelector('.text').outerHTML;
            // add underline elements so we do not need to specify CSS options in the backend's PDF generator
            content = content.replace(/(oov">)(.+?)(<\/span>)/g, '$1<u>$2</u>$3');
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                const authorTitle: string = cc.author + ', ' + cc.title;
                content = `<p>${authorTitle} ${this.corpusService.currentUrn.split(':').slice(-1)[0]}</p>` + content;
                formData.append('html_content', content);
                formData.append('file_type', fileType);
                formData.append('urn', this.corpusService.currentUrn);
                this.isDownloading = true;
                this.helperService.makePostRequest(this.http, this.toastCtrl, this.urlBase, formData).then((response: string) => {
                    this.isDownloading = false;
                    const responseParts: string[] = response.split('.');
                    const link: HTMLLinkElement = document.querySelector(this.downloadLinkSelector);
                    link.href = configMC.backendBaseUrl + configMC.backendApiFilePath + '?id=' + responseParts[0]
                        + '&type=' + responseParts[1];
                    link.style.display = 'block';
                    return resolve();
                }, () => {
                    return reject();
                });
            });
        });
    }

    getWhiteSpace(index: number): string {
        if (this.corpusService.annisResponse.graph_data.nodes[index + 1]) {
            if (this.corpusService.annisResponse.graph_data.nodes[index + 1].annis_tok &&
                this.corpusService.annisResponse.graph_data.nodes[index + 1].annis_tok
                    .search(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g) >= 0) {
                return '';
            }
            return ' ';
        }
        return '';
    }

    ngOnInit(): void {
        this.urlBase = configMC.backendBaseUrl + configMC.backendApiFilePath;
        this.vocService.currentReferenceVocabulary = this.vocService.currentReferenceVocabulary || VocabularyCorpus.bws;
    }
}
