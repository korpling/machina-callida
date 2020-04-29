import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {TestBed, async, ComponentFixture} from '@angular/core/testing';

import {MenuController, Platform} from '@ionic/angular';
import {SplashScreen} from '@ionic-native/splash-screen/ngx';
import {StatusBar} from '@ionic-native/status-bar/ngx';

import {AppComponent} from './app.component';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {AppRoutingModule, routes} from './app-routing.module';
import {
    FakeLoader,
    TranslatePipeMock,
    TranslateServiceStub,
    TranslateTestingModule
} from './translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {Subscription} from 'rxjs';
import {HelperService} from './helper.service';
import {CorpusService} from './corpus.service';
import Spy = jasmine.Spy;
import MockMC from './models/mockMC';
import {LoadChildrenCallback, Route} from '@angular/router';
import configMC from '../configMC';
import {SemanticsPageModule} from './semantics/semantics.module';

describe('AppComponent', () => {
    let statusBarSpy, splashScreenSpy, platformReadySpy, fixture: ComponentFixture<AppComponent>,
        appComponent: AppComponent;

    class PlatformStub {
        backButton = {
            subscribeWithPriority(priority: number, callback: () => (Promise<any> | void)): Subscription {
                return Subscription.EMPTY;
            }
        };
        wasReadyCalled = false;

        public ready(): Promise<any> {
            this.wasReadyCalled = true;
            return Promise.resolve();
        }
    }

    beforeEach(async(() => {
        platformReadySpy = Promise.resolve();
        statusBarSpy = jasmine.createSpyObj('StatusBar', ['styleDefault']);
        splashScreenSpy = jasmine.createSpyObj('SplashScreen', ['hide']);
        TestBed.configureTestingModule({
            declarations: [AppComponent],
            imports: [
                AppRoutingModule,
                HttpClientModule,
                IonicStorageModule.forRoot({name: 'mc_db', driverOrder: ['indexeddb', 'websql', 'localstorage']}),
                TranslateTestingModule
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            providers: [
                {provide: StatusBar, useValue: statusBarSpy},
                {provide: SplashScreen, useValue: splashScreenSpy},
                {provide: Platform, useClass: PlatformStub},
                {provide: APP_BASE_HREF, useValue: '/'},
                {provide: MenuController},
                {provide: CorpusService, useValue: {initCorpusService: () => Promise.resolve()}},
                {
                    provide: HelperService,
                    useValue: {makeGetRequest: () => Promise.resolve(MockMC.apiResponseCorporaGet)}
                }
            ],
        }).compileComponents().then();
        fixture = TestBed.createComponent(AppComponent);
        appComponent = fixture.componentInstance;
    }));

    it('should create the app', () => {
        const app = fixture.debugElement.componentInstance;
        expect(app).toBeTruthy();
    });

    it('should initialize the app', async () => {
        const platformStub: PlatformStub = TestBed.get(Platform);
        expect(platformStub.wasReadyCalled).toBeTruthy();
        await platformReadySpy;
        expect(statusBarSpy.styleDefault).toHaveBeenCalled();
        expect(splashScreenSpy.hide).toHaveBeenCalled();
    });

    it('should close the menu', () => {
        const closeSpy: Spy = spyOn(appComponent.menuCtrl, 'close').and.returnValue(Promise.resolve(true));
        appComponent.closeMenu(true);
        expect(closeSpy).toHaveBeenCalledTimes(1);
    });

    it('should initialize the translations', () => {
        spyOn(appComponent.translate, 'getBrowserLang').and.returnValue(undefined);
        const languageSpy: Spy = spyOn(appComponent.translate, 'getDefaultLang').and.returnValue('de');
        appComponent.initTranslate();
        expect(appComponent.translate.currentLang).toBe('de');
        expect(languageSpy).toHaveBeenCalledTimes(1);
    });

    it('should test routing', (done) => {
        const semanticsRoute: Route = routes.find(x => x.path === configMC.pageUrlSemantics.slice(1));
        const lcb: LoadChildrenCallback = semanticsRoute.loadChildren as LoadChildrenCallback;
        const promise: Promise<any> = lcb() as Promise<any>;
        promise.then((result: any) => {
            expect(result).toBe(SemanticsPageModule);
            done();
        });
    });

    it('should test translations', (done) => {
        const translateService: TranslateServiceStub = new TranslateServiceStub();
        expect(translateService.getDefaultLang()).toBe('en');
        translateService.get('key').subscribe((result: string) => {
            expect(result).toBe('key');
            const translatePipe: TranslatePipeMock = new TranslatePipeMock();
            expect(translatePipe.transform('query')).toBe('query');
            const translateLoader: FakeLoader = new FakeLoader();
            translateLoader.getTranslation('en').subscribe((result2: any) => {
                expect(Object.keys(result2).length).toBe(0);
                done();
            });
        });
    });
});
