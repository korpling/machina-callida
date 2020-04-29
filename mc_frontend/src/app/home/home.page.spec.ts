import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {HomePage} from './home.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import Spy = jasmine.Spy;
import {ToastController} from '@ionic/angular';
import MockMC from '../models/mockMC';

describe('HomePage', () => {
    let homePage: HomePage;
    let fixture: ComponentFixture<HomePage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [HomePage],
            imports: [
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
        fixture = TestBed.createComponent(HomePage);
        homePage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(homePage).toBeTruthy();
    });

    it('should change the language', (done) => {
        const translateSpy: Spy = spyOn(homePage.corpusService, 'adjustTranslations').and.returnValue(Promise.resolve());
        spyOn(homePage.corpusService, 'processAnnisResponse');
        homePage.changeLanguage('').then(() => {
            expect(translateSpy).toHaveBeenCalledTimes(1);
            homePage.changeLanguage('').then(() => {
                expect(translateSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should be initialized', () => {
        const translateSpy: Spy = spyOn(homePage.helperService, 'loadTranslations');
        homePage.ionViewDidEnter();
        expect(translateSpy).toHaveBeenCalledTimes(1);
        homePage.helperService.isIE11 = true;
        homePage.ngOnInit();
        const tabs: HTMLElement = document.querySelector('#tabs') as HTMLElement;
        expect(tabs.style.maxWidth).toBe('65%');
    });

    it('should refresh the corpora', (done) => {
        homePage.isCorpusUpdateInProgress = true;
        const getCorporaSpy: Spy = spyOn(homePage.corpusService, 'getCorpora').and.returnValue(Promise.resolve());
        homePage.refreshCorpora().then(() => {
            expect(homePage.isCorpusUpdateInProgress).toBe(false);
            homePage.isCorpusUpdateInProgress = true;
            getCorporaSpy.and.callFake(() => Promise.reject());
            homePage.refreshCorpora().then(() => {
            }, () => {
                expect(homePage.isCorpusUpdateInProgress).toBe(false);
                done();
            });
        });
    });
});
