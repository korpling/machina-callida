import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {PreviewPage} from './preview.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import {CorpusService} from '../corpus.service';
import {ToastController} from '@ionic/angular';
import MockMC from '../models/mockMC';
import {AnnisResponse} from '../models/annisResponse';
import {Solution} from '../models/solution';
import {ExerciseType} from '../models/enum';
import {SolutionElement} from '../models/solutionElement';
import Spy = jasmine.Spy;
import {NodeMC} from '../models/nodeMC';
import {TestResultMC} from '../models/testResultMC';
import H5PeventDispatcherMock from '../models/h5pEventDispatcherMock';
import Result from '../models/xAPI/Result';
import configMC from '../../configMC';

declare var H5P: any;

describe('PreviewPage', () => {
    let previewPage: PreviewPage;
    let fixture: ComponentFixture<PreviewPage>;
    let corpusService: CorpusService;
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
        corpusService = TestBed.inject(CorpusService);
        fixture = TestBed.createComponent(PreviewPage);
        previewPage = fixture.componentInstance;
        xapiSpy = spyOn(previewPage, 'setXAPIeventHandler');
        checkAnnisResponseSpy = spyOn(corpusService, 'checkAnnisResponse').and.callFake(() => Promise.reject());
        fixture.detectChanges();
    }));

    beforeEach(() => {
    });

    it('should create', () => {
        expect(previewPage).toBeTruthy();
    });

    it('should copy the link', () => {
        previewPage.helperService.isVocabularyCheck = true;
        previewPage.corpusService.annisResponse = new AnnisResponse({solutions: []});
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
        previewPage.corpusService.annisResponse = new AnnisResponse({exercise_id: '', solutions: [new Solution()]});
        previewPage.currentSolutions = previewPage.corpusService.annisResponse.solutions;
        previewPage.initH5P();
        expect(previewPage.solutionIndicesString.length).toBe(0);
        previewPage.exerciseService.excludeOOV = true;
        previewPage.corpusService.exercise.type = ExerciseType.markWords;
        previewPage.initH5P();
        expect(previewPage.solutionIndicesString.length).toBe(21);
    });

    it('should be initialized', (done) => {
        const body: HTMLBodyElement = document.querySelector('body');
        let iframe: HTMLIFrameElement = document.createElement('iframe');
        iframe.setAttribute('id', previewPage.exerciseService.h5pIframeString.slice(1));
        body.appendChild(iframe);
        spyOn(previewPage, 'sendData').and.returnValue(Promise.resolve());
        previewPage.ngOnDestroy();
        const newDispatcher: H5PeventDispatcherMock = new H5PeventDispatcherMock();
        const oldDispatcher: any = previewPage.helperService.deepCopy(H5P.externalDispatcher);
        H5P.externalDispatcher = newDispatcher;
        xapiSpy.and.callThrough();
        previewPage.ngOnInit().then(() => {
            newDispatcher.triggerXAPI(configMC.xAPIverbIDanswered, new Result());
            checkAnnisResponseSpy.and.returnValue(Promise.resolve());
            spyOn(previewPage, 'initH5P');
            spyOn(previewPage, 'processAnnisResponse');
            previewPage.currentSolutions = [new Solution()];
            previewPage.ngOnInit().then(() => {
                expect(previewPage.currentSolutions.length).toBe(0);
                iframe = document.querySelector(previewPage.exerciseService.h5pIframeString);
                iframe.parentNode.removeChild(iframe);
                H5P.externalDispatcher = oldDispatcher;
                done();
            });
        });
    });

    it('should process an ANNIS response', () => {
        previewPage.corpusService.annisResponse = new AnnisResponse({});
        const ar: AnnisResponse = new AnnisResponse({
            solutions: [new Solution({target: new SolutionElement({content: 'content'})})]
        });
        previewPage.processAnnisResponse(ar);
        expect(previewPage.corpusService.annisResponse.solutions.length).toBe(1);
        previewPage.corpusService.currentUrn = 'urn:';
        previewPage.processAnnisResponse(ar);
        expect(previewPage.corpusService.annisResponse.nodes).toEqual(ar.nodes);
    });

    it('should process solutions', () => {
        const solutions: Solution[] = [
            new Solution({
                target: new SolutionElement({content: 'content2', salt_id: 'id'}),
                value: new SolutionElement({salt_id: 'id'})
            }),
            new Solution({
                target: new SolutionElement({content: 'content1', salt_id: 'id'}),
                value: new SolutionElement({salt_id: 'id'})
            }),
            new Solution({
                target: new SolutionElement({content: 'content1', salt_id: 'id'}),
                value: new SolutionElement({salt_id: 'id'})
            }),
            new Solution({
                target: new SolutionElement({content: 'content3', salt_id: 'id'}),
                value: new SolutionElement({salt_id: 'id'})
            })];
        previewPage.corpusService.exercise.type = ExerciseType.markWords;
        previewPage.exerciseService.excludeOOV = true;
        previewPage.corpusService.annisResponse = new AnnisResponse({
            nodes: [new NodeMC({is_oov: false, id: 'id'})],
            solutions
        });
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
        previewPage.currentSolutions = [new Solution()];
        previewPage.corpusService.annisResponse = new AnnisResponse();
        spyOn(previewPage, 'processSolutions');
        spyOn(previewPage, 'initH5P');
        previewPage.switchOOV();
        expect(previewPage.currentSolutions.length).toBe(0);
    });
});
