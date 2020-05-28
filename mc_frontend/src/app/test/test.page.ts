/* tslint:disable:no-string-literal */
import {Component, NgZone, OnDestroy, OnInit} from '@angular/core';
import {NavController, PopoverController, ToastController} from '@ionic/angular';
import {HelperService} from '../helper.service';
import {XAPIevent} from 'src/app/models/xAPIevent';
import {TranslateService} from '@ngx-translate/core';
import {VocabularyService} from 'src/app/vocabulary.service';
import {TestModuleState, TestType} from 'src/app/models/enum';
import {ConfirmCancelPage} from 'src/app/confirm-cancel/confirm-cancel.page';
import {ExercisePart} from 'src/app/models/exercisePart';
import Activity from 'src/app/models/xAPI/Activity';
import LanguageMap from 'src/app/models/xAPI/LanguageMap';
import {HttpClient} from '@angular/common/http';
import Context from 'src/app/models/xAPI/Context';
import {TestResultMC} from 'src/app/models/testResultMC';
import {ExerciseService} from 'src/app/exercise.service';
import configMC from '../../configMC';
import {Storage} from '@ionic/storage';
import {CorpusService} from '../corpus.service';

@Component({
    selector: 'app-test',
    templateUrl: './test.page.html',
    styleUrls: ['./test.page.scss'],
})

export class TestPage implements OnDestroy, OnInit {
    Array = Array;
    Object = Object;
    TestModuleState = TestModuleState;
    TestType = TestType;
    public areEventHandlersSet = false;
    public availableExerciseParts: ExercisePart[] = [new ExercisePart({
        startIndex: 0,
        durationSeconds: 0,
        exercises: ['nonH5P_1']
    }), new ExercisePart({
        /** pretest */
        startIndex: 0,
        durationSeconds: 240,
        exercises: ['fill_blanks_6', 'fill_blanks_1', 'multi_choice_5', 'multi_choice_6',
            'multi_choice_7', 'multi_choice_8', 'fill_blanks_2', 'fill_blanks_7',
            'fill_blanks_4', 'multi_choice_18', 'multi_choice_9']
    }), new ExercisePart({
        /** comprehension exercise */
        startIndex: 0,
        durationSeconds: 1080,
        exercises: ['mark_words_1', 'fill_blanks_11', 'fill_blanks_12', 'fill_blanks_13',
            'fill_blanks_14', 'fill_blanks_16', 'fill_blanks_15', 'multi_choice_24']
    }), new ExercisePart({
        /** cloze text exercise */
        startIndex: 0,
        durationSeconds: 720,
        exercises: ['drag_text_1', 'drag_text_2', 'drag_text_3', 'drag_text_4', 'drag_text_6', 'drag_text_5']
    }), new ExercisePart({
        /** pair association exercise */
        startIndex: 0,
        durationSeconds: 720,
        exercises: HelperService.shuffle(['voc_list_2', 'voc_list_6', 'voc_list_10',
            'voc_list_11', 'voc_list_12', 'voc_list_16',
            'voc_list_17', 'voc_list_18', 'voc_list_27',
            'voc_list_29', 'voc_list_30', 'voc_list_31', 'voc_list_34',
            'voc_list_42', 'voc_list_43', 'voc_list_49', 'voc_list_52',
            'voc_list_53', 'voc_list_54', 'voc_list_56', 'voc_list_61', 'voc_list_62',
            'voc_list_65', 'voc_list_66', 'voc_list_67', 'voc_list_70',
            'voc_list_72', 'voc_list_84', 'voc_list_85', 'voc_list_86',
            'voc_list_87', 'voc_list_88', 'voc_list_89', 'voc_list_90', 'voc_list_91'])
    }), new ExercisePart({
        /** posttest */
        startIndex: 0,
        durationSeconds: 240,
        exercises: ['fill_blanks_6', 'fill_blanks_1', 'multi_choice_5', 'multi_choice_6',
            'multi_choice_7', 'multi_choice_8', 'fill_blanks_2', 'fill_blanks_7',
            'fill_blanks_4', 'multi_choice_18', 'multi_choice_9']
    }), new ExercisePart({exercises: ['nonH5P_2'], startIndex: 0})];
    public configMC = configMC;
    public countDownDateTime: number;
    public currentState: TestModuleState = TestModuleState.inProgress;
    public didTimeRunOut = false;
    public exerciseIndices: number[];
    public finishExerciseTimeout = 200;
    public h5pAnswerClassString = '.h5p-answer';
    public h5pBlanksString = 'H5P.Blanks';
    public h5pCheckButtonClassString = '.h5p-question-check-answer';
    public h5pDragTextString = 'H5P.DragText';
    public h5pKnownIDstring = '#known';
    public h5pMultiChoiceString = 'H5P.MultiChoice';
    public h5pRetryClassString = '.h5p-question-try-again';
    public h5pRowIDstring = '#h5p-row';
    public h5pShowSolutionClassString = '.h5p-question-show-solution';
    public h5pTextInputClassString = '.h5p-text-input';
    public hideClassString = 'hide';
    public isTestMode: boolean;
    public knownCount: [number, number];
    public nonH5Pstring = 'nonH5P';
    public progressBarValue: number;
    public results: [number, number][];
    public resultsBaseIndex: number;
    public testType: TestType;
    public timer: any;
    public timerIDstring = '#timer';
    public timerValueZero = '00m00s';
    public wasDataSent: boolean;

    constructor(public navCtrl: NavController,
                public translate: TranslateService,
                public vocService: VocabularyService,
                public popoverController: PopoverController,
                public http: HttpClient,
                public toastCtrl: ToastController,
                public exerciseService: ExerciseService,
                public storage: Storage,
                public helperService: HelperService,
                public corpusService: CorpusService,
                public ngZone: NgZone) {
    }

    addScore(allTestIndices: number[], exercisePartIndex: number): void {
        const relevantTestIndices = allTestIndices.filter(
            x => this.exerciseService.currentExerciseParts[exercisePartIndex].startIndex <= x &&
                (!this.exerciseService.currentExerciseParts[exercisePartIndex + 1] ||
                    x < this.exerciseService.currentExerciseParts[exercisePartIndex + 1].startIndex));
        const correctlySolved = relevantTestIndices.filter((i) => {
            return this.vocService.currentTestResults[i].statement.result.score.scaled === 1;
        });
        this.results.push([correctlySolved.length, relevantTestIndices.length]);
    }

    adjustStartIndices(): void {
        this.exerciseService.currentExerciseParts[0].startIndex = 0;
        [...Array(this.exerciseService.currentExerciseParts.length).keys()].forEach((index: number) => {
            if (index === 0) {
                return;
            }
            this.exerciseService.currentExerciseParts[index].startIndex = this.exerciseService.currentExerciseParts[index - 1]
                .startIndex + this.exerciseService.currentExerciseParts[index - 1].exercises.length;
        });
    }

    adjustTimer(newIndex: number, review: boolean): void {
        if (!this.isTestMode) {
            return;
        }
        if (!review) {
            const metaIndex: number = this.exerciseService.currentExerciseParts.map(x => x.startIndex).indexOf(newIndex);
            if (metaIndex > -1 && this.exerciseService.currentExerciseParts[metaIndex].durationSeconds > 0) {
                this.removeTimer(false);
                this.initTimer(this.exerciseService.currentExerciseParts[metaIndex].durationSeconds);
            }
        }
        if (newIndex === this.exerciseService.currentExerciseParts[this.exerciseService.currentExerciseParts.length - 1].startIndex) {
            this.removeTimer(true);
        }
    }

    analyzePretestResults(allTestIndices: number[], relevantTestIndices: number[], correctlySolved: number[]): void {
        relevantTestIndices = allTestIndices.filter(x => x < this.exerciseService.currentExerciseParts[this.resultsBaseIndex].startIndex);
        correctlySolved = relevantTestIndices.filter((i) => {
            return this.vocService.currentTestResults[i].statement.result.score.scaled === 1;
        });
        this.results.push([correctlySolved.length, relevantTestIndices.length]);
    }

    analyzeResults(): void {
        this.results = [];
        this.resultsBaseIndex = this.isTestMode ? 2 : 1;
        const allTestIndices: number[] = Object.keys(this.vocService.currentTestResults).map(x => +x);
        let relevantTestIndices: number[] = [];
        let correctlySolved: number[] = [];
        if (this.isTestMode) {
            this.analyzePretestResults(allTestIndices, relevantTestIndices, correctlySolved);
        }
        // text comprehension
        this.addScore(allTestIndices, this.resultsBaseIndex);
        // exercises
        relevantTestIndices = allTestIndices.filter(x => this.exerciseService.currentExerciseParts[this.resultsBaseIndex + 1].startIndex
            <= x && x < this.exerciseService.currentExerciseParts[this.resultsBaseIndex + 2].startIndex);
        correctlySolved = relevantTestIndices.map(i => this.vocService.currentTestResults[i].statement.result.score.raw);
        const scoreObserved: number = correctlySolved.length ? correctlySolved.reduce((x, y) => x + y) : 0;
        const scoreExpected: number = relevantTestIndices.length ? relevantTestIndices.map(
            i => this.vocService.currentTestResults[i].statement.result.score.max).reduce((x, y) => x + y) : 0;
        this.results.push([scoreObserved, scoreExpected]);
        // posttest
        this.addScore(allTestIndices, this.resultsBaseIndex + 2);
        this.currentState = TestModuleState.showResults;
    }

    attemptExit(ev: any = null): Promise<void> {
        return new Promise<void>(async (resolve) => {
            this.helperService.currentPopover = await this.popoverController.create({
                component: ConfirmCancelPage,
                event: ev,
                translucent: true
            });
            this.helperService.currentPopover.present().then();
            return resolve();
        });
    }

    continueToNextExercise(isTestMode: boolean = true): void {
        // this needs to run in the angular zone to update data bindings in the view immediately
        this.ngZone.run(() => {
            if (this.isTestMode && !isTestMode) {
                // no pretest in learning mode
                this.deleteExercisePart(1);
            }
            this.isTestMode = isTestMode;
            this.exerciseService.currentExerciseIndex = this.exerciseService.currentExerciseIndex + 1;
            this.showNextExercise(this.exerciseService.currentExerciseIndex,
                this.currentState === TestModuleState.showSolutions).then();
        });
    }

    deleteExercisePart(index: number): void {
        this.exerciseIndices = [];
        this.exerciseService.currentExerciseParts.splice(index, 1);
        this.adjustStartIndices();
        // dirty hack to make the view re-render any ngFor references to the exerciseIndices
        setTimeout(() => {
            const exerciseCount: number = this.exerciseService.currentExerciseParts.map(x => x.exercises.length)
                .reduce((x, y) => x + y);
            this.exerciseIndices = Array.from(new Array(exerciseCount).keys());
        }, 50);
    }

    finishCurrentExercise(event: XAPIevent): Promise<void> {
        return new Promise<void>(resolve => {
            if (!this.isTestMode) {
                this.saveCurrentExerciseResult(false, event);
                return resolve();
            }
            // hide H5P immediately so the solutions are not visible to the user
            document.querySelector(this.h5pRowIDstring).classList.add(this.hideClassString);
            // dirty hack to wait for the solutions being processed by H5P
            setTimeout(() => {
                this.saveCurrentExerciseResult(true, event);
                if (!this.didTimeRunOut) {
                    this.continueToNextExercise();
                }
                return resolve();
            }, this.finishExerciseTimeout);
        });
    }

    hideRetryButton(): void {
        const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
        const iframeDoc: Document = iframe.contentWindow.document;
        // hide the retry button during review
        const retryButton: HTMLButtonElement = iframeDoc.documentElement.querySelector(this.h5pRetryClassString);
        if (retryButton) {
            retryButton.style.display = 'none';
        }
    }

    initTimer(durationSeconds: number): void {
        // add the new duration to countdown
        this.countDownDateTime = new Date(new Date().getTime() + durationSeconds * 1000).getTime();
        // Update the countdown every 1 second
        this.timer = setInterval(this.updateTimer.bind(this), 1000);
    }

    ngOnDestroy(): void {
        this.removeTimer(false);
        this.helperService.getH5P().externalDispatcher.off('xAPI');
        this.helperService.getH5P().externalDispatcher.off('domChanged');
    }

    ngOnInit(): void {
        this.isTestMode = true;
        this.randomizeTestType();
        this.results = [];
        this.wasDataSent = false;
        this.exerciseService.currentExerciseIndex = 0;
        this.vocService.currentTestResults = {};
        this.currentState = TestModuleState.inProgress;
        this.knownCount = [0, 0];
        this.setH5PeventHandlers();
        const h5pRow = document.querySelector(this.h5pRowIDstring);
        if (h5pRow) {
            h5pRow.classList.add(this.hideClassString);
        }
    }

    randomizeTestType(): void {
        this.exerciseService.currentExerciseParts = this.availableExerciseParts.slice();
        // remove either the second last or third last exercise
        const index: number = Math.random() < 0.5 ? 3 : 4;
        this.testType = index === 3 ? TestType.cloze : TestType.list;
        this.deleteExercisePart(this.exerciseService.currentExerciseParts.length - index);
    }

    removeTimer(freeze: boolean): void {
        const timerElement: HTMLSpanElement = document.querySelector(this.timerIDstring);
        clearInterval(this.timer);
        if (timerElement && !freeze) {
            timerElement.innerHTML = this.timerValueZero;
        }
    }

    resetTestEnvironment(): void {
        this.ngOnDestroy();
        this.ngOnInit();
    }

    saveCurrentExerciseResult(showSolutions: boolean, event: XAPIevent): void {
        const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
        if (iframe) {
            const iframeDoc: Document = iframe.contentWindow.document;
            const inner: string = iframeDoc.documentElement.innerHTML;
            this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex] = new TestResultMC({
                statement: event.data.statement,
                innerHTML: inner
            });
            const knownCheckbox: HTMLInputElement = iframeDoc.querySelector(this.h5pKnownIDstring);
            if (knownCheckbox) {
                this.knownCount = [this.knownCount[0] + (knownCheckbox.checked ? 1 : 0), this.knownCount[1] + 1];
            }
            if (showSolutions) {
                const solutionButton: HTMLButtonElement = iframeDoc.querySelector(this.h5pShowSolutionClassString);
                if (solutionButton) {
                    solutionButton.click();
                }
            }
        }
    }

    sendData(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            if (this.wasDataSent) {
                this.helperService.showToast(this.toastCtrl, this.corpusService.dataAlreadySentMessage).then();
                return resolve();
            }
            const fileUrl: string = configMC.backendBaseUrl + configMC.backendApiFilePath;
            const formData = new FormData();
            // tslint:disable-next-line:prefer-const
            let learningResult: object = {};
            Object.keys(this.vocService.currentTestResults)
                .forEach(i => learningResult[i] = this.vocService.currentTestResults[i].statement);
            formData.append('learning_result', JSON.stringify(learningResult));
            this.helperService.makePostRequest(this.http, this.toastCtrl, fileUrl, formData).then(async () => {
                this.wasDataSent = true;
                this.helperService.showToast(this.toastCtrl, this.corpusService.dataSentSuccessMessage).then();
                return resolve();
            }, () => {
                return reject();
            });
        });
    }

    setH5PeventHandlers(): void {
        this.helperService.getH5P().externalDispatcher.on('xAPI', (event: XAPIevent) => {
            if (this.currentState !== TestModuleState.inProgress) {
                return;
            }
            // results are only available when a task has been completed/answered, not in the "attempted" or "interacted" stages
            if (event.data.statement.verb.id === configMC.xAPIverbIDanswered && event.data.statement.result) {
                this.finishCurrentExercise(event).then();
            }
        });
        this.helperService.getH5P().externalDispatcher.on('domChanged', (event: any) => {
            // dirty hack because domChanged events are triggered twice for every new H5P exercise
            if (!this.areEventHandlersSet) {
                if (this.currentState === TestModuleState.inProgress && event.data.library === this.h5pBlanksString) {
                    this.setInputEventHandler();
                } else if (this.currentState === TestModuleState.showSolutions) {
                    this.triggerSolutionsEventHandler();
                }
            }
            this.areEventHandlersSet = !this.areEventHandlersSet;
        });
    }

    setInputEventHandler(): void {
        const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
        if (iframe) {
            const inputs: NodeList = iframe.contentWindow.document.querySelectorAll(this.h5pTextInputClassString);
            inputs.forEach((input: HTMLInputElement) => {
                input.addEventListener('keydown', (event: KeyboardEvent) => {
                    if (event.key === 'Enter') {
                        // Cancel the default action, if needed
                        event.preventDefault();
                        const checkButton: HTMLButtonElement = iframe.contentWindow.document.body.querySelector(
                            this.h5pCheckButtonClassString);
                        if (checkButton && !this.didTimeRunOut) {
                            // prevent the check button from jumping to the next exercise
                            checkButton.click();
                        }
                    }
                }, {passive: false});
            });
        }
    }

    showNextExercise(newIndex: number, review: boolean = false): Promise<void> {
        return new Promise<void>(resolve => {
            this.adjustTimer(newIndex, review);
            const currentExercisePart: ExercisePart = this.exerciseService.currentExerciseParts
                [this.exerciseService.currentExercisePartIndex];
            const maxProgress: number = currentExercisePart.exercises.length;
            this.progressBarValue = (newIndex - currentExercisePart.startIndex) / maxProgress;
            if (this.exerciseService.currentExerciseName.startsWith(this.nonH5Pstring)) {
                document.querySelector(this.h5pRowIDstring).classList.add(this.hideClassString);
                if (newIndex ===
                    this.exerciseService.currentExerciseParts[this.exerciseService.currentExerciseParts.length - 1].startIndex) {
                    this.analyzeResults();
                    this.helperService.getH5P().externalDispatcher.off('xAPI');
                }
                return resolve();
            }
            this.currentState = review ? TestModuleState.showSolutions : TestModuleState.inProgress;
            document.querySelector(this.h5pRowIDstring).classList.remove(this.hideClassString);
            if (review && this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]) {
                const id = this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]
                    .statement.context.contextActivities.category[0].id;
                // handle the drag text exercise solutions
                if (id.indexOf(this.h5pDragTextString) > -1) {
                    const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
                    const iframeDoc: Document = iframe.contentWindow.document;
                    iframeDoc.documentElement.innerHTML = this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]
                        .innerHTML;
                    this.hideRetryButton();
                    return resolve();
                }
            }
            const fileName: string = this.exerciseService.currentExerciseName.split('_').slice(-1) + '_' +
                this.translate.currentLang + '.json';
            let exerciseType = this.exerciseService.currentExerciseName.split('_').slice(0, 2).join('_');
            this.exerciseService.setH5Purl(this.helperService.baseUrl + '/assets/h5p/' + exerciseType + '/content/' + fileName);
            if (exerciseType.startsWith(this.exerciseService.vocListString)) {
                exerciseType = this.exerciseService.fillBlanksString;
            }
            this.exerciseService.initH5P(exerciseType).then(() => {
                return resolve();
            });
        });
    }

    triggerSolutionsEventHandler(): void {
        const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
        if (iframe) {
            if (this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]) {
                const oldActivity: Activity = this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]
                    .statement.object as Activity;
                const oldContext: Context = this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex].statement.context;
                const oldResponse: string = this.vocService.currentTestResults[this.exerciseService.currentExerciseIndex]
                    .statement.result.response;
                const singleResponses: string[] = oldResponse.split('[,]');
                if (oldContext.contextActivities.category[0].id.indexOf(this.h5pMultiChoiceString) > -1) {
                    const oldChosen: { description: LanguageMap, id: string }[] = oldActivity.definition.choices.filter(
                        x => singleResponses.indexOf(x.id) > -1);
                    const oldCheckedStrings: string[] = oldChosen.map(x => x.description[Object.keys(x.description)[0]]);
                    const newOptions: NodeListOf<HTMLUListElement> = iframe.contentWindow.document.querySelectorAll(
                        this.h5pAnswerClassString);
                    newOptions.forEach((newOption: HTMLUListElement) => {
                        if (oldCheckedStrings.indexOf(newOption.innerText.slice(0, -1)) > -1) {
                            newOption.click();
                        }
                    });
                } else if (oldContext.contextActivities.category[0].id.indexOf(this.h5pBlanksString) > -1) {
                    const inputs: NodeList = iframe.contentWindow.document.querySelectorAll(this.h5pTextInputClassString);
                    inputs.forEach((input: HTMLInputElement, index: number) => {
                        input.value = singleResponses[index];
                    });
                } else if (oldContext.contextActivities.category[0].id.indexOf(this.h5pDragTextString) > -1) {
                    // this case is handled elsewhere because we cannot fake the drag text exercises easily
                }
            }
            const checkButton: HTMLButtonElement = iframe.contentWindow.document.body.querySelector(this.h5pCheckButtonClassString);
            if (checkButton) {
                // prevent the check button from jumping to the next exercise
                checkButton.click();
                this.hideRetryButton();
            }
        }
    }

    public updateTimer(): void {
        // Get today's date and time
        const now = new Date().getTime();
        // Find the distance between now and the countdown date
        const distance = this.countDownDateTime - now;
        // Time calculations for minutes and seconds
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        // Output the result in an element with the corresponding ID
        const timerElement: HTMLSpanElement = document.querySelector(this.timerIDstring);
        if (timerElement) {
            timerElement.innerHTML = minutes + 'm' + seconds + 's ';
        }
        // If the count down is over, write some text
        if (distance < 0) {
            this.removeTimer(false);
            const iframe: HTMLIFrameElement = document.querySelector(this.exerciseService.h5pIframeString);
            if (iframe) {
                const checkButton: HTMLButtonElement = iframe.contentWindow.document.body.querySelector(this.h5pCheckButtonClassString);
                if (checkButton) {
                    // prevent the check button from jumping to the next exercise
                    this.didTimeRunOut = true;
                    checkButton.click();
                    // dirty hack to wait for the XAPI handlers
                    setTimeout(() => {
                        this.didTimeRunOut = false;
                    }, this.finishExerciseTimeout);
                }
            }
            const newIndex: number = this.exerciseService.currentExerciseParts[this.exerciseService.currentExercisePartIndex + 1]
                .startIndex;
            this.exerciseService.currentExerciseIndex = newIndex;
            this.showNextExercise(newIndex).then();
        }
    }
}
