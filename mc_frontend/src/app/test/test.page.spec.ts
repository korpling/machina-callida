import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, fakeAsync, TestBed, tick} from '@angular/core/testing';

import {TestPage} from './test.page';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {PopoverController} from '@ionic/angular';
import {APP_BASE_HREF} from '@angular/common';
import {TestResultMC} from '../models/testResultMC';
import StatementBase from '../models/xAPI/StatementBase';
import Result from '../models/xAPI/Result';
import Score from '../models/xAPI/Score';
import {EventMC, TestModuleState} from '../models/enum';
import MockMC from '../models/mockMC';
import {XAPIevent} from '../models/xAPIevent';
import EventRegistry from '../models/eventRegistry';
import Verb from '../models/xAPI/Verb';
import configMC from '../../configMC';
import Context from '../models/xAPI/Context';
import ContextActivities from '../models/xAPI/ContextActivities';
import Activity from '../models/xAPI/Activity';
import Definition from '../models/xAPI/Definition';
import {HttpClientModule} from '@angular/common/http';
import {By} from '@angular/platform-browser';
import Spy = jasmine.Spy;
import {ExerciseTypePath} from '../../../openapi';

describe('TestPage', () => {
    let testPage: TestPage;
    let fixture: ComponentFixture<TestPage>;
    let newDispatcher: EventRegistry;
    let getH5Pspy: Spy;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [TestPage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
                {provide: PopoverController, useValue: MockMC.popoverController},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        });
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TestPage);
        testPage = fixture.componentInstance;
        newDispatcher = new EventRegistry();
        getH5Pspy = spyOn(testPage.helperService, 'getH5P').and.returnValue({externalDispatcher: newDispatcher});
        fixture.detectChanges();
    });

    afterEach(() => {
        fixture.destroy();
    });

    it('should create', () => {
        expect(testPage).toBeTruthy();
    });

    it('should adjust the timer', () => {
        testPage.isTestMode = false;
        const timerElement: HTMLSpanElement = fixture.debugElement.query(By.css(testPage.timerIDstring)).nativeElement;
        timerElement.innerHTML = '1';
        testPage.adjustTimer(1, false);
        expect(document.querySelector(testPage.timerIDstring).innerHTML).toBe('1');
        testPage.isTestMode = true;
        testPage.adjustTimer(testPage.exerciseService.currentExerciseParts[testPage.exerciseService.currentExerciseParts.length - 1]
            .startIndex, true);
        expect(document.querySelector(testPage.timerIDstring).innerHTML).toBe('1');
        testPage.adjustTimer(1, false);
        expect(document.querySelector(testPage.timerIDstring).innerHTML).toBe(testPage.timerValueZero);
    });

    it('should analyze results', () => {
        testPage.isTestMode = false;
        testPage.currentState = TestModuleState.inProgress;
        testPage.vocService.currentTestResults = testPage.helperService.deepCopy(MockMC.testResults);
        testPage.analyzeResults();
        expect(testPage.results.length).toBe(3);
        testPage.vocService.currentTestResults[21] = new TestResultMC({
            statement: new StatementBase({result: new Result({score: new Score({scaled: 0, raw: 0})})})
        });
        testPage.vocService.currentTestResults[5] = testPage.vocService.currentTestResults[21];
        testPage.isTestMode = true;
        testPage.analyzeResults();
        expect(testPage.results.length).toBe(4);
    });

    it('should continue to the next exercise', () => {
        spyOn(testPage, 'showNextExercise').and.returnValue(Promise.resolve());
        testPage.exerciseService.currentExerciseIndex = 0;
        testPage.continueToNextExercise(false);
        expect(testPage.exerciseService.currentExerciseIndex).toBe(1);
    });

    it('should attempt to exit', (done) => {
        testPage.helperService.currentPopover = null;
        testPage.attemptExit().then(() => {
            expect(testPage.helperService.currentPopover).toBeTruthy();
            done();
        });
    });

    it('should finish the current exercise', (done) => {
        testPage.isTestMode = false;
        spyOn(testPage, 'saveCurrentExerciseResult');
        const continueSpy: Spy = spyOn(testPage, 'continueToNextExercise');
        testPage.finishCurrentExercise(new XAPIevent()).then(() => {
            expect(continueSpy).toHaveBeenCalledTimes(0);
            testPage.isTestMode = true;
            testPage.finishCurrentExercise(new XAPIevent()).then(() => {
                expect(continueSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should get the current exercise name', () => {
        testPage.exerciseService.currentExerciseIndex = 10;
        const name: string = testPage.exerciseService.currentExerciseName;
        expect(name.length).toBe(15);
    });

    it('should handle the solutions event', () => {
        const hideButtonSpy: Spy = spyOn(testPage, 'hideRetryButton');
        const iframe: HTMLIFrameElement = document.createElement('iframe');
        spyOn(testPage.exerciseService, 'getH5PIframe').and.returnValue(iframe);
        const checkButton: HTMLButtonElement = document.createElement('button');
        const getSpy: Spy = spyOn(testPage.exerciseService, 'getH5Pelements')
            .withArgs(testPage.h5pCheckButtonClassString).and.returnValue(checkButton);
        testPage.exerciseService.currentExerciseIndex = 0;
        const description = 'description';
        testPage.vocService.currentTestResults[0] = new TestResultMC({
            statement: new StatementBase({
                context: new Context({
                    contextActivities: new ContextActivities({category: [new Activity({id: testPage.h5pMultiChoiceString})]})
                }),
                object: new Activity({
                    definition: new Definition({choices: [{description: {'en-US': description}, id: 'id'}]})
                }),
                result: new Result({response: 'id'})
            })
        });
        const ul: HTMLUListElement = document.createElement('ul');
        ul.innerText = description + 's';
        const clickSpy: Spy = spyOn(ul, 'click');
        getSpy.withArgs(testPage.h5pAnswerClassString, true).and.returnValue([ul]);
        testPage.handleSolutionsEvent();
        expect(clickSpy).toHaveBeenCalledTimes(1);
        testPage.vocService.currentTestResults[0].statement.context.contextActivities.category[0].id = testPage.h5pBlanksString;
        const input: HTMLInputElement = document.createElement('input');
        getSpy.withArgs(testPage.h5pTextInputClassString, true).and.returnValue([input]);
        testPage.handleSolutionsEvent();
        expect(input.value).toBe(testPage.vocService.currentTestResults[0].statement.result.response);
        testPage.vocService.currentTestResults[0].statement.context.contextActivities.category[0].id = testPage.h5pDragTextString;
        testPage.handleSolutionsEvent();
        expect(hideButtonSpy).toHaveBeenCalledTimes(3);
    });

    it('should hide the retry button', () => {
        const retryButton: HTMLButtonElement = document.createElement('button');
        retryButton.style.display = 'block';
        spyOn(testPage.exerciseService, 'getH5Pelements').and.returnValue(retryButton);
        testPage.hideRetryButton();
        expect(retryButton.style.display).toBe('none');
    });

    it('should initialize the timer', () => {
        spyOn(testPage, 'updateTimer');
        testPage.timer = null;
        testPage.initTimer(5);
        expect(testPage.timer).toBeTruthy();
        clearInterval(testPage.timer);
    });

    it('should reset the test environment', () => {
        testPage.exerciseService.currentExerciseIndex = 1;
        testPage.resetTestEnvironment();
        expect(testPage.exerciseService.currentExerciseIndex).toBe(0);
    });

    it('should save the current result', () => {
        const iframe: HTMLIFrameElement = MockMC.addIframe(testPage.exerciseService.h5pIframeString);
        spyOn(testPage.exerciseService, 'getH5PIframe').and.returnValue(iframe);
        const knownCheckbox: HTMLInputElement = document.createElement('input');
        const solutionButton: HTMLButtonElement = document.createElement('button');
        const getSpy: Spy = spyOn(testPage.exerciseService, 'getH5Pelements').withArgs(testPage.h5pKnownIDstring)
            .and.returnValue(knownCheckbox);
        getSpy.withArgs(testPage.h5pShowSolutionClassString).and.returnValue(solutionButton);
        testPage.exerciseService.currentExerciseIndex = 5;
        testPage.knownCount = [0, 0];
        testPage.saveCurrentExerciseResult(true, new XAPIevent({data: {statement: new StatementBase()}}));
        expect(testPage.knownCount[0]).toBe(0);
        knownCheckbox.checked = true;
        testPage.saveCurrentExerciseResult(true, new XAPIevent({data: {statement: new StatementBase()}}));
        expect(testPage.knownCount[0]).toBe(1);
        iframe.parentNode.removeChild(iframe);
    });

    it('should send data', (done) => {
        testPage.wasDataSent = false;
        testPage.vocService.currentTestResults[0] = new TestResultMC();
        const requestSpy: Spy = spyOn(testPage.helperService, 'makePostRequest').and.callFake(() => Promise.reject());
        testPage.sendData().then(() => {
        }, () => {
            expect(requestSpy).toHaveBeenCalledTimes(1);
            requestSpy.and.returnValue(Promise.resolve());
            testPage.sendData().then(() => {
                expect(testPage.wasDataSent).toBe(true);
                expect(requestSpy).toHaveBeenCalledTimes(2);
                testPage.sendData().then(() => {
                    expect(requestSpy).toHaveBeenCalledTimes(2);
                    done();
                });
            });
        });
    });

    it('should set H5P event handlers', () => {
        const finishSpy: Spy = spyOn(testPage, 'finishCurrentExercise').and.returnValue(Promise.resolve());
        testPage.currentState = TestModuleState.showResults;
        const xapiEvent: XAPIevent = new XAPIevent({
            data: {
                statement: new StatementBase({result: new Result(), verb: new Verb({id: configMC.xAPIverbIDanswered})})
            }
        });
        newDispatcher.trigger(EventMC.xAPI, xapiEvent);
        expect(finishSpy).toHaveBeenCalledTimes(0);
        testPage.currentState = TestModuleState.inProgress;
        newDispatcher.trigger(EventMC.xAPI, xapiEvent);
        expect(finishSpy).toHaveBeenCalledTimes(1);
        const inputEventSpy: Spy = spyOn(testPage, 'setInputEventHandler');
        const solutionsEventSpy: Spy = spyOn(testPage, 'handleSolutionsEvent');
        testPage.currentState = TestModuleState.inProgress;
        const domChangedEvent: any = {data: {library: testPage.fillBlanksString}};
        testPage.helperService.events.trigger(EventMC.h5pCreated, domChangedEvent);
        expect(inputEventSpy).toHaveBeenCalledTimes(1);
        testPage.currentState = TestModuleState.showSolutions;
        testPage.helperService.events.trigger(EventMC.h5pCreated, domChangedEvent);
        expect(solutionsEventSpy).toHaveBeenCalledTimes(1);
    });

    it('should set the input event handler', () => {
        const checkButton: HTMLButtonElement = document.createElement('button');
        const clickSpy: Spy = spyOn(checkButton, 'click');
        const getSpy: Spy = spyOn(testPage.exerciseService, 'getH5Pelements')
            .withArgs(testPage.h5pCheckButtonClassString).and.returnValue(checkButton);
        const input: HTMLInputElement = document.createElement('input');
        getSpy.withArgs(testPage.h5pTextInputClassString, true).and.returnValue([input]);
        testPage.setInputEventHandler();
        const kbe: KeyboardEvent = new KeyboardEvent('keydown', {key: 'Enter'});
        input.dispatchEvent(kbe);
        expect(clickSpy).toHaveBeenCalledTimes(1);
    });

    it('should show the next exercise', (done) => {
        spyOn(testPage, 'handleSolutionsEvent');
        const resultsSpy: Spy = spyOn(testPage, 'analyzeResults');
        const hideButtonSpy: Spy = spyOn(testPage, 'hideRetryButton');
        let targetExercisePartIndex: number = testPage.exerciseService.currentExerciseParts
            .findIndex(x => x.exercises.some(y => y.startsWith(ExerciseTypePath.VocList)));
        if (targetExercisePartIndex < 0) {
            testPage.exerciseService.currentExerciseParts.push(testPage.availableExerciseParts[4]);
            testPage.adjustStartIndices();
            targetExercisePartIndex = testPage.exerciseService.currentExerciseParts.length - 1;
        }
        const previousExercises: number[] = testPage.exerciseService.currentExerciseParts.slice(0, targetExercisePartIndex)
            .map(x => x.exercises.length);
        testPage.exerciseService.currentExerciseIndex = previousExercises.reduce((a, b) => a + b);
        testPage.helperService.events.on(EventMC.h5pCreated, async (event: any) => {
            expect(event.data.library).toBe(ExerciseTypePath.FillBlanks);
            testPage.helperService.events.off(EventMC.h5pCreated);
            testPage.vocService.currentTestResults[2] = new TestResultMC({
                statement: new StatementBase({
                    context: new Context({
                        contextActivities: new ContextActivities({category: [new Activity({id: testPage.h5pDragTextString})]})
                    })
                })
            });
            testPage.exerciseService.currentExerciseIndex = 2;
            const iframe: HTMLIFrameElement = MockMC.addIframe(testPage.exerciseService.h5pIframeString);
            fixture.detectChanges();
            await testPage.showNextExercise(2, true);
            expect(hideButtonSpy).toHaveBeenCalledTimes(1);
            testPage.exerciseService.currentExerciseName = testPage.nonH5Pstring;
            await testPage.showNextExercise(testPage.exerciseService.currentExerciseParts
                [testPage.exerciseService.currentExerciseParts.length - 1].startIndex);
            expect(resultsSpy).toHaveBeenCalledTimes(1);
            iframe.parentElement.removeChild(iframe);
            done();
        });
        spyOn(testPage.exerciseService, 'createH5Pstandalone').and.returnValue(Promise.resolve());
        testPage.showNextExercise(testPage.exerciseService.currentExerciseIndex).then();
    });

    it('should update the timer', fakeAsync(() => {
        testPage.countDownDateTime = new Date().getTime() - 1;
        const checkButton: HTMLButtonElement = document.createElement('button');
        spyOn(testPage.exerciseService, 'getH5Pelements').and.returnValue(checkButton);
        const showNextSpy: Spy = spyOn(testPage, 'showNextExercise').and.returnValue(Promise.resolve());
        testPage.updateTimer();
        expect(showNextSpy).toHaveBeenCalledTimes(1);
        tick(testPage.finishExerciseTimeout);
    }));
});
