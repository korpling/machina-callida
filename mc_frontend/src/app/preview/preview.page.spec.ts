import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {PreviewPage} from './preview.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import {ToastController} from '@ionic/angular';
import MockMC from '../models/mockMC';
import {EventMC, ExerciseType} from '../models/enum';
import Spy = jasmine.Spy;
import {TestResultMC} from '../models/testResultMC';
import EventRegistry from '../models/eventRegistry';
import Result from '../models/xAPI/Result';
import configMC from '../../configMC';
import {AnnisResponse, Solution} from '../../../openapi';
import {XAPIevent} from '../models/xAPIevent';
import StatementBase from '../models/xAPI/StatementBase';
import Verb from '../models/xAPI/Verb';

describe('PreviewPage', () => {
    let previewPage: PreviewPage;
    let fixture: ComponentFixture<PreviewPage>;
    let checkAnnisResponseSpy: Spy;
    let xapiSpy: Spy;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [PreviewPage],
            imports: [
                FormsModule,
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
                {provide: ToastController, useValue: MockMC.toastController}
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(PreviewPage);
        previewPage = fixture.componentInstance;
        xapiSpy = spyOn(previewPage, 'setXAPIeventHandler');
        checkAnnisResponseSpy = spyOn(previewPage.corpusService, 'checkAnnisResponse').and.callFake(() => Promise.reject());
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(previewPage).toBeTruthy();
    });

    it('should copy the link', () => {
        previewPage.helperService.isVocabularyCheck = true;
        previewPage.corpusService.annisResponse = {solutions: []};
        fixture.detectChanges();
        const button: HTMLIonButtonElement = document.querySelector('#showShareLinkButton');
        button.click();
        fixture.detectChanges();
        previewPage.copyLink();
        const input: HTMLInputElement = document.querySelector(previewPage.inputSelector);
        expect(input.selectionStart).toBe(0);
        expect(input.selectionEnd).toBe(0);
    });

    it('should initialize H5P', () => {
        spyOn(previewPage.exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        previewPage.corpusService.annisResponse = {exercise_id: '', solutions: [{}]};
        previewPage.currentSolutions = previewPage.corpusService.annisResponse.solutions;
        previewPage.initH5P();
        expect(previewPage.solutionIndicesString.length).toBe(0);
        previewPage.exerciseService.excludeOOV = true;
        previewPage.corpusService.exercise.type = ExerciseType.markWords;
        previewPage.initH5P();
        expect(previewPage.solutionIndicesString.length).toBe(19);
    });

    it('should be initialized', (done) => {
        const body: HTMLBodyElement = document.querySelector('body');
        let iframe: HTMLIFrameElement = document.createElement('iframe');
        iframe.classList.add(previewPage.exerciseService.h5pIframeString.slice(1));
        body.appendChild(iframe);
        spyOn(previewPage, 'sendData').and.returnValue(Promise.resolve());
        previewPage.ngOnDestroy();
        const newDispatcher: EventRegistry = new EventRegistry();
        spyOn(previewPage.helperService, 'getH5P').and.returnValue({externalDispatcher: newDispatcher});
        xapiSpy.and.callThrough();
        previewPage.ngOnInit().then(() => {
            newDispatcher.trigger(EventMC.xAPI, new XAPIevent({
                data: {
                    statement: new StatementBase({
                        result: new Result(),
                        verb: new Verb({id: configMC.xAPIverbIDanswered})
                    })
                }
            }));
            checkAnnisResponseSpy.and.returnValue(Promise.resolve());
            spyOn(previewPage, 'initH5P');
            spyOn(previewPage, 'processAnnisResponse');
            previewPage.currentSolutions = [{}];
            previewPage.ngOnInit().then(() => {
                expect(previewPage.currentSolutions.length).toBe(0);
                iframe = document.querySelector(previewPage.exerciseService.h5pIframeString);
                iframe.parentNode.removeChild(iframe);
                done();
            });
        });
    });

    it('should process an ANNIS response', () => {
        previewPage.corpusService.annisResponse = {graph_data: {links: [], nodes: []}};
        const solution: Solution = {target: {content: 'content', sentence_id: 1, token_id: 1}};
        const ar: AnnisResponse = {solutions: [solution], graph_data: {links: [], nodes: []}};
        previewPage.processAnnisResponse(ar);
        expect(previewPage.corpusService.annisResponse.solutions.length).toBe(1);
        previewPage.corpusService.currentUrn = 'urn:';
        previewPage.processAnnisResponse(ar);
        expect(previewPage.corpusService.annisResponse.graph_data.nodes).toEqual(ar.graph_data.nodes);
    });

    it('should process solutions', () => {
        const solutions: Solution[] = [
            {
                target: {content: 'content2', salt_id: 'id', sentence_id: 1, token_id: 1},
                value: {salt_id: 'id', content: '', sentence_id: 1, token_id: 1}
            },
            {
                target: {content: 'content1', salt_id: 'id', sentence_id: 1, token_id: 1},
                value: {salt_id: 'id', content: '', sentence_id: 1, token_id: 1}
            },
            {
                target: {content: 'content1', salt_id: 'id', sentence_id: 1, token_id: 1},
                value: {salt_id: 'id', content: '', sentence_id: 1, token_id: 1}
            },
            {
                target: {content: 'content3', salt_id: 'id', sentence_id: 1, token_id: 1},
                value: {salt_id: 'id', content: '', sentence_id: 1, token_id: 1}
            }];
        previewPage.corpusService.exercise.type = ExerciseType.markWords;
        previewPage.exerciseService.excludeOOV = true;
        previewPage.corpusService.annisResponse = {
            graph_data: {nodes: [{is_oov: false, id: 'id'}], links: []},
            solutions
        };
        previewPage.processSolutions(solutions);
        expect(previewPage.currentSolutions[2]).toBe(solutions[0]);
    });

    it('should send data', (done) => {
        const requestSpy: Spy = spyOn(previewPage.helperService, 'makePostRequest').and.returnValue(Promise.resolve());
        const consoleSpy: Spy = spyOn(console, 'log');
        previewPage.sendData(new TestResultMC()).then(() => {
            expect(consoleSpy).toHaveBeenCalledTimes(0);
            requestSpy.and.callFake(() => Promise.reject());
            previewPage.sendData(new TestResultMC()).then(() => {
            }, () => {
                expect(consoleSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should switch OOV', () => {
        previewPage.currentSolutions = [{}];
        previewPage.corpusService.annisResponse = {};
        spyOn(previewPage, 'processSolutions');
        spyOn(previewPage, 'initH5P');
        previewPage.switchOOV();
        expect(previewPage.currentSolutions.length).toBe(0);
    });
});
