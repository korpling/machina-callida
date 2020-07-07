/* tslint:disable:no-string-literal */
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {NavController, ToastController} from '@ionic/angular';
import {ApplicationState} from 'src/app/models/applicationState';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';
import {CaseValue, DependencyValue, PartOfSpeechValue} from 'src/app/models/enum';
import {TranslateService} from '@ngx-translate/core';
import {Storage} from '@ionic/storage';
import {Language} from 'src/app/models/language';
import {ReplaySubject} from 'rxjs';
import {TextData} from './models/textData';
import configMC from '../configMC';
import EventRegistry from './models/eventRegistry';

declare var H5P: any;
// dirty hack to prevent H5P access errors after resize events
window.onresize = () => {
    /* tslint:disable:prefer-const */
    /* tslint:disable:no-shadowed-variable */
    let H5P: any;
    /* tslint:enable:prefer-const */
    /* tslint:enable:no-shadowed-variable */
};

@Injectable({
    providedIn: 'root'
})
export class HelperService {
    public static generalErrorAlertMessage: string;
    public applicationState: ReplaySubject<ApplicationState> = null;
    public applicationStateCache: ApplicationState = null;
    public baseUrl: string = location.protocol.concat('//').concat(window.location.host) +
        window.location.pathname.split('/').slice(0, -1).join('/');
    public caseMap: { [rawValue: string]: CaseValue } = {
        Nom: CaseValue.nominative,
        Gen: CaseValue.genitive,
        Dat: CaseValue.dative,
        Acc: CaseValue.accusative,
        Abl: CaseValue.ablative,
        Voc: CaseValue.vocative,
        Loc: CaseValue.locative,
    };
    public corpusUpdateCompletedString: string;
    public currentError: HttpErrorResponse;
    public currentLanguage: Language;
    public currentPopover: HTMLIonPopoverElement;
    public dependencyMap: { [rawValue: string]: DependencyValue } = {
        acl: DependencyValue.adjectivalClause,
        advcl: DependencyValue.adverbialClauseModifier,
        advmod: DependencyValue.adverbialModifier,
        amod: DependencyValue.adjectivalModifier,
        appos: DependencyValue.appositionalModifier,
        aux: DependencyValue.auxiliary,
        'aux:pass': DependencyValue.auxiliary,
        case: DependencyValue.caseMarking,
        cc: DependencyValue.coordinatingConjunction,
        ccomp: DependencyValue.clausalComplement,
        clf: DependencyValue.classifier,
        compound: DependencyValue.multiwordExpression,
        conj: DependencyValue.conjunct,
        cop: DependencyValue.copula,
        csubj: DependencyValue.subject,
        'csubj:pass': DependencyValue.subject,
        det: DependencyValue.determiner,
        discourse: DependencyValue.discourseElement,
        dislocated: DependencyValue.dislocated,
        expl: DependencyValue.expletive,
        fixed: DependencyValue.multiwordExpression,
        flat: DependencyValue.multiwordExpression,
        goeswith: DependencyValue.goesWith,
        iobj: DependencyValue.object,
        list: DependencyValue.list,
        mark: DependencyValue.marker,
        nmod: DependencyValue.nominalModifier,
        'nmod:poss': DependencyValue.nominalModifier,
        nummod: DependencyValue.numericModifier,
        nsubj: DependencyValue.subject,
        'nsubj:pass': DependencyValue.subject,
        obj: DependencyValue.object,
        obl: DependencyValue.oblique,
        orphan: DependencyValue.orphan,
        parataxis: DependencyValue.parataxis,
        punct: DependencyValue.punctuation,
        root: DependencyValue.root,
        vocative: DependencyValue.vocative,
        xcomp: DependencyValue.clausalComplement,
    };
    public events: EventRegistry = new EventRegistry();
    public isIE11: boolean = !!(window as any).MSInputMethodContext && !!(document as any).documentMode;
    public isDevMode = ['localhost'].indexOf(window.location.hostname) > -1; // set this to "false" for simulated production mode
    public isVocabularyCheck = false;
    public languages: Language[] = [
        new Language({name: 'English', shortcut: 'en'}),
        new Language({name: 'Deutsch', shortcut: 'de'})];
    public openRequests: string[] = [];
    public partOfSpeechMap: { [rawValue: string]: PartOfSpeechValue } = {
        ADJ: PartOfSpeechValue.adjective,
        ADP: PartOfSpeechValue.preposition,
        ADV: PartOfSpeechValue.adverb,
        AUX: PartOfSpeechValue.auxiliary,
        CCONJ: PartOfSpeechValue.conjunction,
        DET: PartOfSpeechValue.pronoun,
        INTJ: PartOfSpeechValue.interjection,
        NOUN: PartOfSpeechValue.noun,
        NUM: PartOfSpeechValue.numeral,
        PART: PartOfSpeechValue.particle,
        PRON: PartOfSpeechValue.pronoun,
        PROPN: PartOfSpeechValue.properNoun,
        PUNCT: PartOfSpeechValue.punctuation,
        SCONJ: PartOfSpeechValue.conjunction,
        SYM: PartOfSpeechValue.symbol,
        VERB: PartOfSpeechValue.verb,
        X: PartOfSpeechValue.other
    };

    constructor(public http: HttpClient,
                public storage: Storage,
                public translate: TranslateService,
    ) {
        this.initConfig();
        this.initLanguage();
        this.initApplicationState();
    }

    // The translate loader needs to know where to load i18n files in Ionic's static asset pipeline.
    static createTranslateLoader(http: HttpClient): TranslateHttpLoader {
        return new TranslateHttpLoader(http, './assets/i18n/', '.json');
    }

    /**
     * Shuffles array in place.
     * @param array items An array containing the items.
     */
    static shuffle(array: Array<any>): Array<any> {
        let j, x, i;
        for (i = array.length - 1; i > 0; i--) {
            j = Math.floor(Math.random() * (i + 1));
            x = array[i];
            array[i] = array[j];
            array[j] = x;
        }
        return array;
    }

    deepCopy(obj: object): any {
        let copy;
        // Handle the 3 simple types, and null or undefined
        if (null === obj || 'object' !== typeof obj) {
            return obj;
        }
        // Handle Date
        if (obj instanceof Date) {
            copy = new Date();
            copy.setTime(obj.getTime());
            return copy;
        }
        // Handle Array
        if (obj instanceof Array) {
            copy = [];
            for (let i = 0, len = obj.length; i < len; i++) {
                copy[i] = this.deepCopy(obj[i]);
            }
            return copy;
        }
        // Handle Object
        if (obj instanceof Object) {
            copy = {};
            for (const attr in obj) {
                if (obj.hasOwnProperty(attr)) {
                    copy[attr] = this.deepCopy(obj[attr]);
                }
            }
            return copy;
        }
    }

    getDelayedTranslation(translate: TranslateService, key: string) {
        return new Promise(resolve => {
            translate.get(key).subscribe((value: string) => {
                // check if we got the correct translated value
                if (value === value.toUpperCase()) {
                    setTimeout(() => {
                        translate.get(key).subscribe(value2 => resolve(value2));
                    }, 1000);
                } else {
                    resolve(value);
                }
            });
        });
    }

    getEnumValues(target: any): string[] {
        return Object.keys(target).filter((value, index, array) => {
            return index % 2 !== 0;
        });
    }

    getH5P(): any {
        return H5P;
    }

    goToAuthorDetailPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlAuthorDetail);
    }

    goToAuthorPage(navCtrl: NavController): Promise<boolean> {
        this.isVocabularyCheck = false;
        return navCtrl.navigateForward(configMC.pageUrlAuthor);
    }

    goToDocExercisesPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlDocExercises);
    }

    goToDocSoftwarePage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlDocSoftware);
    }

    goToDocVocUnitPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlDocVocUnit);
    }

    goToExerciseListPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlExerciseList);
    }

    goToExerciseParametersPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlExerciseParameters);
    }

    goToHomePage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateRoot(configMC.pageUrlHome);
    }

    goToImprintPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlImprint);
    }

    goToInfoPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlInfo);
    }

    goToKwicPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlKwic);
    }

    goToPreviewPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlPreview);
    }

    goToRankingPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlRanking);
    }

    goToSemanticsPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlSemantics);
    }

    goToShowTextPage(navCtrl: NavController, isVocabularyCheck: boolean = false): Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            navCtrl.navigateForward(configMC.pageUrlShowText).then((result: boolean) => {
                this.isVocabularyCheck = isVocabularyCheck;
                return resolve(result);
            });
        });
    }

    goToSourcesPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlSources);
    }

    goToTestPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateRoot(configMC.pageUrlTest);
    }

    goToTextRangePage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlTextRange);
    }

    goToVocabularyCheckPage(navCtrl: NavController): Promise<boolean> {
        return navCtrl.navigateForward(configMC.pageUrlVocabularyCheck);
    }

    handleRequestError(toastCtrl: ToastController, error: HttpErrorResponse, errorMessage: string, url: string): void {
        this.openRequests.splice(this.openRequests.indexOf(url), 1);
        this.currentError = error;
        this.showToast(toastCtrl, errorMessage).then();
    }

    initApplicationState(): void {
        this.applicationState = new ReplaySubject<ApplicationState>(1);
        if (!this.applicationStateCache) {
            this.storage.get(configMC.localStorageKeyApplicationState).then((jsonString: string) => {
                this.applicationStateCache = new ApplicationState({
                    currentSetup: new TextData(),
                    exerciseList: []
                });
                if (jsonString) {
                    const jsonObject: any = this.updateAnnisResponse(jsonString);
                    const state: ApplicationState = jsonObject as ApplicationState;
                    state.exerciseList = state.exerciseList ? state.exerciseList : [];
                    this.applicationStateCache = state;
                }
                this.applicationState.next(this.applicationStateCache);
            });
        } else {
            this.applicationState.next(this.applicationStateCache);
        }
    }

    initConfig(): void {
        if (!configMC.backendBaseUrl) {
            const part1: string = location.protocol.concat('//').concat(window.location.host);
            configMC.backendBaseUrl = part1.concat(configMC.backendBaseApiPath).concat('/');
        }
        if (!configMC.frontendBaseUrl) {
            configMC.frontendBaseUrl = location.protocol.concat('//').concat(window.location.host);
        }
    }

    initLanguage(): void {
        // dirty hack to wait for the translateService intializing
        setTimeout(() => {
            this.currentLanguage = this.languages.find(x => x.shortcut === this.translate.currentLang);
            this.loadTranslations(this.translate);
        });
    }

    loadTranslations(translate: TranslateService): void {
        // dirty hack to wait until the translation loader is initialized in IE11
        this.getDelayedTranslation(translate, 'CORPUS_UPDATE_COMPLETED').then((value: string) => {
            this.corpusUpdateCompletedString = value;
        });
        this.getDelayedTranslation(translate, 'ERROR_GENERAL_ALERT').then((value: string) => {
            HelperService.generalErrorAlertMessage = value;
        });
    }

    makeGetRequest(http: HttpClient, toastCtrl: ToastController, url: string, params: HttpParams,
                   errorMessage: string = HelperService.generalErrorAlertMessage): Promise<any> {
        return new Promise(((resolve, reject) => {
            this.currentError = null;
            this.openRequests.push(url);
            http.get(url, {params}).subscribe((result: any) => {
                this.openRequests.splice(this.openRequests.indexOf(url), 1);
                return resolve(result);
            }, async (error: HttpErrorResponse) => {
                this.handleRequestError(toastCtrl, error, errorMessage, url);
                return reject(error);
            });
        }));
    }

    makePostRequest(http: HttpClient, toastCtrl: ToastController, url: string, formData: FormData,
                    errorMessage: string = HelperService.generalErrorAlertMessage): Promise<any> {
        return new Promise(((resolve, reject) => {
            this.currentError = null;
            this.openRequests.push(url);
            http.post(url, formData).subscribe((result: any) => {
                this.openRequests.splice(this.openRequests.indexOf(url), 1);
                return resolve(result);
            }, async (error: HttpErrorResponse) => {
                this.handleRequestError(toastCtrl, error, errorMessage, url);
                return reject(error);
            });
        }));
    }

    saveApplicationState(state: ApplicationState): Promise<void> {
        return new Promise((resolve) => {
            this.applicationStateCache = state;
            this.applicationState.next(this.applicationStateCache);
            this.storage.set(configMC.localStorageKeyApplicationState, JSON.stringify(state)).then(() => {
                return resolve();
            });
        });
    }

    showToast(toastCtrl: ToastController, message: string, position: any = 'top'): Promise<void> {
        return toastCtrl.create({
            message,
            duration: 3000,
            position
        }).then((toast: HTMLIonToastElement) => toast.present());
    }

    updateAnnisResponse(jsonString: string): any {
        const jsonObject: any = JSON.parse(jsonString);
        // backwards compatibility
        [jsonObject.currentSetup, jsonObject.mostRecentSetup].forEach((textdata: any) => {
            if (textdata && textdata.annisResponse && !textdata.annisResponse.graph_data) {
                const annisResp: any = textdata.annisResponse;
                const props: string[] = ['links', 'nodes', 'directed', 'graph', 'multigraph'];
                annisResp.graph_data = {};
                props.forEach((prop: string) => {
                    annisResp.graph_data[prop] = annisResp[prop];
                    delete annisResp[prop];
                });
            }
        });
        return jsonObject;
    }
}
